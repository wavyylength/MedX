import sys
import os
from PIL import Image
import torch
from torchvision import models, transforms
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import cv2

# ===================================================================
#                          CONFIGURATION
# ===================================================================

# 📌
# 📌 ===> 1. REPLACE THIS WITH THE PATH TO YOUR X-RAY IMAGE <===
# 📌
IMAGE_PATH =  r"C:\Users\Prince Kumar\Desktop\hackathon\MedX\explainable_xray\data\x2.jpeg"

# The 10 disease classes the model identifies.
CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema"
]

# ===================================================================
#                         MODEL DEFINITION
# ===================================================================

class CustomDenseNet(models.DenseNet):
    """
    A custom DenseNet class that overrides the forward pass to ensure
    the final ReLU operation is "out-of-place". This is crucial for
    making Grad-CAM compatible with this architecture.
    """
    def forward(self, x):
        features = self.features(x)
        # The key change from the original: inplace=False
        out = F.relu(features, inplace=False)
        out = F.adaptive_avg_pool2d(out, (1, 1))
        out = torch.flatten(out, 1)
        out = self.classifier(out)
        return out

def load_model():
    """Initializes the custom DenseNet model and loads pretrained weights."""
    print("🧠 Loading pre-trained DenseNet-121 model...")
    # These are the standard parameters for DenseNet-121
    model = CustomDenseNet(
        growth_rate=32,
        block_config=(6, 12, 24, 16),
        num_init_features=64,
        bn_size=4,
        drop_rate=0
    )
    # Load weights from the standard pre-trained model
    pretrained_state_dict = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT).state_dict()
    model.load_state_dict(pretrained_state_dict)
    model.eval()
    print("✅ Model loaded successfully.")
    return model

# ===================================================================
#                  IMAGE & GRAD-CAM FUNCTIONS
# ===================================================================

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

    # Register hooks on the final feature block
    last_feature_block = model.features
    h1 = last_feature_block.register_forward_hook(forward_hook)
    h2 = last_feature_block.register_full_backward_hook(backward_hook)

    input_tensor.requires_grad_(True)
    model.zero_grad()
    
    output = model(input_tensor)
    loss = output[0, target_class]
    loss.backward()

    # Get the feature maps and gradients captured by the hooks
    feature_map = features[0][0].detach()
    grads = gradients[0][0].detach()

    # Calculate neuron importance weights and create heatmap
    weights = torch.mean(grads, dim=[1, 2])
    cam = torch.zeros(feature_map.shape[1:], dtype=torch.float32)
    for i, w in enumerate(weights):
        cam += w * feature_map[i, :, :]

    # Post-process the heatmap
    cam = cam.cpu().numpy()
    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (224, 224))
    if np.max(cam) > 0:
        cam = (cam - np.min(cam)) / np.max(cam)
    
    h1.remove()
    h2.remove()
    return cam

# ===================================================================
#                        ANALYSIS & VISUALIZATION
# ===================================================================

def analyze_xray(image_path, model):
    """
    Performs the full analysis pipeline on a single chest X-ray image.
    """
    print(f"\n🩺 Analyzing image: {os.path.basename(image_path)}")
    x_tensor, orig_img = preprocess_image(image_path)
    if x_tensor is None:
        return
        
    # Get model predictions
    with torch.no_grad():
        pred = torch.sigmoid(model(x_tensor))
    
    pred = pred.cpu().numpy()[0][:len(CLASSES)]
    results = {label: float(prob) for label, prob in zip(CLASSES, pred)}

    # --- Print detected diseases ---
    threshold = 0.5
    detected = {k: v for k, v in results.items() if v > threshold}
    print("-" * 40)
    if detected:
        print("⚠️ Pathologies detected:")
        for disease, prob in sorted(detected.items(), key=lambda item: item[1], reverse=True):
            print(f"   - {disease}: {prob*100:.1f}% confidence")
    else:
        print(f"✅ No pathologies detected above {threshold*100}% threshold.")
    print("-" * 40)

    # --- Display probability bar chart ---
    plt.figure(figsize=(10, 5))
    plt.bar(results.keys(), [v * 100 for v in results.values()], color='#1f77b4')
    plt.ylim(0, 100)
    plt.ylabel("Confidence (%)")
    plt.title(f"Predicted Probabilities for '{os.path.basename(image_path)}'")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

    # --- Display Grad-CAM heatmaps for detected diseases ---
    if detected:
        print("\n🔥 Generating Grad-CAM heatmaps...")
        for disease in detected:
            idx = CLASSES.index(disease)
            # Re-create tensor for gradient calculation
            x_for_grad, _ = preprocess_image(image_path)
            
            cam = generate_gradcam(model, x_for_grad, idx)

            if cam is not None:
                plt.figure(figsize=(8, 8))
                plt.imshow(orig_img, cmap='gray')
                plt.imshow(cam, cmap='jet', alpha=0.5)
                plt.title(f"Grad-CAM: {disease}")
                plt.axis('off')
                plt.show()

# ===================================================================
#                           SCRIPT EXECUTION
# ===================================================================

def main():
    """The main function to run the script."""
    # Check if the placeholder path is still being used
    if "path/to/your" in IMAGE_PATH:
        print("=" * 60)
        print("🚨 ACTION REQUIRED 🚨")
        print("\nPlease edit this script and update the 'IMAGE_PATH' variable on line 24")
        print("with the actual file path to your chest X-ray image.")
        print("=" * 60)
        return
    
    # Load the model and run the analysis
    model = load_model()
    analyze_xray(IMAGE_PATH, model)


if __name__ == "__main__":
    main()