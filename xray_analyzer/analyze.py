import torch
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

from utils import preprocess_image

CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema"
]

def generate_gradcam(model, input_tensor, target_class, original_image_np):
    model.eval()
    features, gradients = [], []

    def forward_hook(module, input, output): features.append(output)
    def backward_hook(module, grad_in, grad_out): gradients.append(grad_out[0])

    last_conv_layer = None
    for layer in reversed(list(model.features.modules())):
        if isinstance(layer, torch.nn.Conv2d):
            last_conv_layer = layer
            break
    
    if not last_conv_layer: return None

    h1 = last_conv_layer.register_forward_hook(forward_hook)
    h2 = last_conv_layer.register_full_backward_hook(backward_hook)

    input_tensor.requires_grad_(True)
    model.zero_grad()
    output = model(input_tensor)
    loss = output[0, target_class]
    loss.backward()

    feature_map = features[0][0].detach()
    grads = gradients[0][0].detach()

    weights = torch.mean(grads, dim=[1, 2])
    cam = torch.zeros(feature_map.shape[1:], dtype=torch.float32)
    for i, w in enumerate(weights):
        cam += w * feature_map[i, :, :]

    cam = torch.maximum(cam, torch.tensor(0.0)).cpu().numpy()
    if np.max(cam) > 0: cam = cam / np.max(cam)
    
    h1.remove(); h2.remove()
    
    heatmap = cv2.resize(cam, (original_image_np.shape[1], original_image_np.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    original_image_bgr = cv2.cvtColor(np.array(original_image_np), cv2.COLOR_RGB2BGR)
    superimposed_img = cv2.addWeighted(original_image_bgr, 0.6, heatmap, 0.4, 0)
    
    return superimposed_img

def get_predictions_for_api(image_path, model):
    x_tensor, original_image = preprocess_image(image_path)
    if x_tensor is None: return None, None
        
    with torch.no_grad():
        pred = torch.sigmoid(model(x_tensor))
    
    pred = pred.cpu().numpy()[0][:len(CLASSES)]
    results = {label: float(prob) for label, prob in zip(CLASSES, pred)}
    
    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    predictions_json = [{"name": label, "confidence": round(prob * 100)} for label, prob in sorted_results]
    
    heatmaps_json = []
    detected_diseases = [p for p in predictions_json if p['confidence'] > 50]

    if detected_diseases:
        for disease in detected_diseases:
            target_class_index = CLASSES.index(disease['name'])
            superimposed_img = generate_gradcam(model, x_tensor, target_class_index, np.array(original_image))
            
            if superimposed_img is not None:
                is_success, buffer = cv2.imencode(".png", superimposed_img)
                if is_success:
                    img_bytes = BytesIO(buffer)
                    base64_string = base64.b64encode(img_bytes.read()).decode()
                    heatmaps_json.append({"disease": disease['name'], "image": base64_string})

    return predictions_json, heatmaps_json