import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2

def preprocess_image(image_path):
    """Loads and transforms an image for model input."""
    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        print(f"❌ Error: Image file not found at '{image_path}'")
        return None, None
        
    # Standard ImageNet transformations
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Return the tensor for the model and a resized version of the original image for plotting
    return transform(image).unsqueeze(0), np.array(image.resize((224, 224)))

def generate_gradcam(model, input_tensor, target_class):
    """Generates the Grad-CAM heatmap for a specific class."""
    features = []
    gradients = []

    def forward_hook(module, input, output):
        features.append(output.clone())

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0].clone())

    last_feature_block = model.features
    h1 = last_feature_block.register_forward_hook(forward_hook)
    h2 = last_feature_block.register_full_backward_hook(backward_hook)

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

    cam = cam.cpu().numpy()
    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (224, 224))
    if np.max(cam) > 0:
        cam = (cam - np.min(cam)) / np.max(cam)
    
    h1.remove()
    h2.remove()
    return cam