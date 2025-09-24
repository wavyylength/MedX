import os
import torch
import matplotlib.pyplot as plt
from utils import preprocess_image, generate_gradcam

CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema"
]

def analyze_xray(image_path, model):
    """
    Performs the full analysis pipeline on a single chest X-ray image.
    """
    print(f"\n🩺 Analyzing image: {os.path.basename(image_path)}")
    x_tensor, orig_img = preprocess_image(image_path)
    if x_tensor is None:
        return
        
    with torch.no_grad():
        pred = torch.sigmoid(model(x_tensor))
    
    pred = pred.cpu().numpy()[0][:len(CLASSES)]
    results = {label: float(prob) for label, prob in zip(CLASSES, pred)}

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

    _plot_probabilities(results, os.path.basename(image_path))
    
    if detected:
        print("\n🔥 Generating Grad-CAM heatmaps...")
        _plot_heatmaps(detected, image_path, model, orig_img)

def _plot_probabilities(results, filename):
    """Helper function to plot the bar chart of probabilities."""
    plt.figure(figsize=(10, 5))
    plt.bar(results.keys(), [v * 100 for v in results.values()], color='#1f77b4')
    plt.ylim(0, 100)
    plt.ylabel("Confidence (%)")
    plt.title(f"Predicted Probabilities for '{filename}'")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def _plot_heatmaps(detected, image_path, model, orig_img):
    """Helper function to generate and plot Grad-CAM heatmaps."""
    for disease in detected:
        idx = CLASSES.index(disease)
        x_for_grad, _ = preprocess_image(image_path)
        
        cam = generate_gradcam(model, x_for_grad, idx)

        if cam is not None:
            plt.figure(figsize=(8, 8))
            plt.imshow(orig_img, cmap='gray')
            plt.imshow(cam, cmap='jet', alpha=0.5)
            plt.title(f"Grad-CAM: {disease}")
            plt.axis('off')
            plt.show()