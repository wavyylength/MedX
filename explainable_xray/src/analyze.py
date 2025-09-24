# src/analyze_image_with_heatmap.py
from PIL import Image
import torch
from torchvision import models, transforms
import numpy as np
import matplotlib.pyplot as plt
import cv2

# --------------------------
# CONFIG
# --------------------------
classes = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema"
]

# --------------------------
# MODEL
# --------------------------
model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
model.eval()

# --------------------------
# IMAGE PREPROCESSING
# --------------------------
def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.485,0.485],[0.229,0.229,0.229])
    ])
    return transform(image).unsqueeze(0), np.array(image)  # return original as numpy

# --------------------------
# GRAD-CAM FUNCTION
# --------------------------
def generate_gradcam(model, input_tensor, target_class):
    """
    Returns heatmap of model focus for a given class index.
    """
    # Forward pass
    features = []
    gradients = []

    def forward_hook(module, input, output):
        features.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    # Register hooks to last convolutional layer
    last_conv = model.features[-1]
    h1 = last_conv.register_forward_hook(forward_hook)
    h2 = last_conv.register_backward_hook(backward_hook)

    model.zero_grad()
    output = model(input_tensor)
    # For multi-label, pick target class
    loss = output[0, target_class]
    loss.backward()

    # Get hooked outputs
    feature_map = features[0][0].detach().numpy()  # [C,H,W]
    grads = gradients[0][0].detach().numpy()  # [C,H,W]

    # Global average pooling of gradients
    weights = np.mean(grads, axis=(1,2))  # [C]
    cam = np.zeros(feature_map.shape[1:], dtype=np.float32)  # [H,W]
    for i, w in enumerate(weights):
        cam += w * feature_map[i]
    cam = np.maximum(cam, 0)  # ReLU
    cam = cv2.resize(cam, (224,224))
    cam = cam - np.min(cam)
    cam = cam / (np.max(cam) + 1e-8)  # normalize 0-1

    # Remove hooks
    h1.remove()
    h2.remove()

    return cam

# --------------------------
# ANALYZE FUNCTION
# --------------------------
def analyze_image(image_path, show_graph=True, show_heatmap=True):
    x, orig_img = preprocess_image(image_path)
    
    with torch.no_grad():
        pred = torch.sigmoid(model(x))
    
    pred = pred.cpu().numpy()[0][:10]  # top 10 classes
    results = {label: float(prob) for label, prob in zip(classes, pred)}
    
    # Print detected diseases
    threshold = 0.5
    detected = {k:v for k,v in results.items() if v > threshold}
    if detected:
        print("⚠️ Detected Diseases:")
        for disease, prob in detected.items():
            print(f"{disease}: {prob*100:.1f}% confidence")
    else:
        print("✅ No disease above threshold detected")

    # Bar chart
    if show_graph:
        labels = list(results.keys())
        confidences = [v*100 for v in results.values()]
        colors = ['red' if v>50 else 'yellow' if v>30 else 'green' for v in confidences]
        plt.figure(figsize=(8,4))
        plt.bar(labels, confidences, color=colors)
        plt.ylim(0,100)
        plt.ylabel("Confidence (%)")
        plt.title("Predicted Probabilities for Top 10 Chest Diseases")
        for idx, conf in enumerate(confidences):
            plt.text(idx, conf + 2, f"{conf:.1f}%", ha='center')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # Heatmap overlay for top predicted disease
    if show_heatmap and detected:
        top_class = list(detected.keys())[0]
        top_idx = classes.index(top_class)
        cam = generate_gradcam(model, x, top_idx)

        plt.figure(figsize=(6,6))
        plt.imshow(orig_img, cmap='gray')
        plt.imshow(cam, cmap='jet', alpha=0.5)  # overlay
        plt.title(f"Grad-CAM Heatmap: {top_class}")
        plt.axis('off')
        plt.show()

    return results

# --------------------------
# EXAMPLE USAGE
# --------------------------
if __name__ == "__main__":
    analyze_image("data/sample_xray.jpg")
