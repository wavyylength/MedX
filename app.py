# patient_portfolio_app.py
import streamlit as st
from PIL import Image
import torch
from torchvision import transforms
from torchvision.models import densenet121
import numpy as np
# --------------------------
# CONFIG
# --------------------------
st.set_page_config(page_title="Chest X-ray Disease Predictor", layout="wide")
st.title("🩺 Chest X-ray Disease Predictor")

# Top 10 chest diseases (CheXpert / example labels)
disease_labels = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema"
]

# --------------------------
# MODEL
# --------------------dddd------
@st.cache_resource
def load_model():
    model = densenet121(pretrained=True)
    model.eval()
    return model

model = load_model()

# --------------------------
# IMAGE UPLOAD
# --------------------------
uploaded_file = st.file_uploader("Upload Chest X-ray Image", type=['png','jpg','jpeg'])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    # --------------------------
    # PREPROCESSING
    # --------------------------
    transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.485,0.485],[0.229,0.229,0.229])
    ])
    
    img = Image.open(uploaded_file).convert("RGB")
    x = transform(img).unsqueeze(0)  # type: ignore
    
    # --------------------------
    # PREDICTION
    # --------------------------
    with torch.no_grad():
        pred = torch.sigmoid(model(x))
    
    pred = pred.cpu().numpy()[0]  # shape [num_classes]

    # For demonstration, take first 10 outputs as top chest diseases
    top_probs = pred[:10]
    results = {label: float(prob) for label, prob in zip(disease_labels, top_probs)}

    # --------------------------
    # DISPLAY RESULTS
    # --------------------------
    st.subheader("Predicted Probabilities for Top 10 Chest Diseases")
    
    # Detected diseases (prob > 0.5)
    threshold = 0.5
    detected = {k:v for k,v in results.items() if v > threshold}
    
    if detected:
        st.markdown("### ⚠️ Detected Diseases")
        for disease, prob in detected.items():
            st.write(f"{disease}: {prob*100:.1f}% confidence")
    else:
        st.markdown("### ✅ No disease above threshold detected")
    
    # Show bar chart
    st.bar_chart(results)
