import streamlit as st
from PIL import Image
import os
from tempfile import NamedTemporaryFile
import base64

# Import your project's modules
from src.model import load_model
from src.analyze import get_predictions, create_probability_fig, create_heatmap_figs

# =================================================================================================
# --- PAGE CONFIGURATION ---
# =================================================================================================

st.set_page_config(
    page_title="Med-AI | Advanced X-Ray Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================================================================
# --- CUSTOM STYLING (CSS) ---
# =================================================================================================

def load_css():
    """Injects custom CSS for a premium look and feel."""
    st.markdown("""
    <style>
        /* --- General App Styling --- */
        .stApp {
            background-color: #EAF2F8; /* Light Sky Blue background */
        }

        /* --- Main Title & Header --- */
        .main-header {
            font-size: 2.5rem;
            color: #1B4F72; /* Dark Sapphire Blue */
            text-align: center;
            font-weight: 700;
            padding-top: 20px;
        }
        
        .main-subheader {
            text-align: center;
            color: #5D6D7E;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }

        /* --- Sidebar Styling --- */
        .css-1d391kg { /* Main sidebar container */
            background-color: #FFFFFF;
            border-right: 2px solid #D6EAF8;
        }
        .sidebar-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1B4F72;
            padding-top: 20px;
        }
        .stFileUploader {
            border: 2px dashed #3498DB;
            border-radius: 10px;
            padding: 15px;
            background-color: #FBFCFC;
        }

        /* --- Card Containers --- */
        .card {
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.05);
            margin: 15px 0;
            transition: all 0.3s ease-in-out;
        }
        .card:hover {
            box-shadow: 0 12px 24px rgba(0,0,0,0.1);
            transform: translateY(-5px);
        }
        .card-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1B4F72;
            margin-bottom: 15px;
        }

        /* --- Custom Buttons & Links --- */
        .stButton>button {
            border-radius: 10px;
            border: 2px solid #3498DB;
            background-color: #3498DB;
            color: white;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: white;
            color: #3498DB;
        }

        /* --- Expander / Accordion Styling --- */
        .stExpander {
            border: none;
            box-shadow: none;
            background-color: #FDFEFE;
            border-radius: 10px;
        }
        .stExpander header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1B4F72;
        }
        
        /* --- Horizontal Line --- */
        hr {
            margin: 30px 0;
            border-top: 2px solid #3498DB;
            opacity: 0.5;
        }
    </style>
    """, unsafe_allow_html=True)

# Call the function to apply CSS
load_css()


# =================================================================================================
# --- MODEL LOADING (CACHED) ---
# =================================================================================================

@st.cache_resource
def load_cached_model():
    """Caches the model to avoid reloading, shows a spinner."""
    with st.spinner('Initializing AI Engine... Please wait.'):
        model = load_model()
    return model

model = load_cached_model()

# =================================================================================================
# --- ASSET & HELPER FUNCTIONS ---
# =================================================================================================

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Using an animated GIF for the sidebar
# In a real app, you would have this file locally. For this example, we'll skip adding a file.
# st.sidebar.image("path/to/your/logo.gif") 


# =================================================================================================
# --- UI RENDERING FUNCTIONS FOR EACH PAGE ---
# =================================================================================================

def render_analyzer_page():
    """Renders the main X-Ray analysis tool."""
    
    # --- SIDEBAR FOR UPLOAD ---
    with st.sidebar:
        st.markdown("<p class='sidebar-header'>Image Upload</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Select a chest radiograph...", 
            type=["png", "jpg", "jpeg"]
        )

    # --- MAIN CONTENT AREA ---
    if uploaded_file is not None:
        # Save uploaded file to a temporary path
        with NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            temp_image.write(uploaded_file.getvalue())
            temp_path = temp_image.name

        # --- ANALYSIS DASHBOARD ---
        col1, col2 = st.columns([0.45, 0.55])

        with col1:
            st.markdown("<div class='card-title'>Uploaded Radiograph</div>", unsafe_allow_html=True)
            image = Image.open(uploaded_file)
            st.image(image, caption='Patient X-Ray', use_container_width=True, output_format='PNG')
        
        with col2:
            with st.spinner('🤖 AI is performing a deep analysis...'):
                results, orig_img = get_predictions(temp_path, model)
                
                if results:
                    threshold = 0.5
                    detected = {k: v for k, v in results.items() if v > threshold}
                    
                    st.markdown("<div class='card-title'>Comprehensive Analysis Report</div>", unsafe_allow_html=True)
                    if detected:
                        st.write("The model has identified the following potential pathologies with confidence levels above 50%:")
                        sorted_detected = sorted(detected.items(), key=lambda item: item[1], reverse=True)
                        for disease, prob in sorted_detected:
                            st.warning(f"**{disease}**: Detected with **{prob*100:.1f}%** confidence.")
                    else:
                        st.success("✅ **Normal Finding:** The model did not detect any of the targeted pathologies above the 50% confidence threshold.")
                    
                    st.markdown("---")
                    st.subheader("Full Probability Distribution")
                    prob_fig = create_probability_fig(results, uploaded_file.name)
                    st.pyplot(prob_fig)
        
        # --- GRAD-CAM VISUALIZATION SECTION ---
        if results and detected:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<p class='main-header' style='font-size: 2rem;'>Explainable AI (XAI) Visualizations</p>", unsafe_allow_html=True)
            st.info("💡 The highlighted areas (heatmaps) below show which parts of the X-ray the AI model focused on to make its predictions for each detected condition. This provides transparency into the AI's decision-making process.")
            
            with st.spinner('Generating visual explanations...'):
                heatmap_figs = create_heatmap_figs(detected.keys(), temp_path, model, orig_img)
                
                num_heatmaps = len(heatmap_figs)
                if num_heatmaps > 0:
                    # Dynamically create columns for a clean, responsive layout
                    max_cols = 3
                    cols = st.columns(min(num_heatmaps, max_cols))
                    col_idx = 0
                    for disease, fig in heatmap_figs.items():
                        with cols[col_idx]:
                            st.pyplot(fig, use_container_width=True)
                        col_idx = (col_idx + 1) % max_cols
        
        os.remove(temp_path)

    else:
        # --- WELCOME SCREEN ---
        st.info('👈 **Get Started:** Upload an X-ray image using the sidebar.')
        st.markdown(
            """
            <div class='card'>
                <div class='card-title'>Welcome to the Med-AI Analyzer 🚀</div>
                <p>This powerful tool leverages deep learning to provide a preliminary analysis of chest radiographs. Our goal is to assist medical professionals by highlighting potential areas of concern and providing transparent, visual explanations for our AI's findings.</p>
                
                <h4>How to Use:</h4>
                <ol>
                    <li><strong>Upload Image:</strong> Use the file uploader in the sidebar to select a PNG, JPG, or JPEG image.</li>
                    <li><strong>Review Report:</strong> The AI will process the image and generate a detailed report, including confidence scores for various pathologies.</li>
                    <li><strong>Explore Visualizations:</strong> For any detected condition, a Grad-CAM heatmap will show the AI's area of focus, offering crucial insight into its decision process.</li>
                </ol>
                
                <p style='font-size: 0.9rem; color: #85929E; text-align: center; margin-top: 20px;'>
                    <strong>Disclaimer:</strong> This tool is for informational and educational purposes only and is not a substitute for diagnosis by a qualified medical professional.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_about_page():
    """Renders the 'About the Technology' page."""
    st.markdown("<div class='card-title'>The Technology Behind Med-AI</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='card'>
        <h4>🧠 The Model: DenseNet-121</h4>
        <p>At the core of this analyzer is a **DenseNet-121** model, a state-of-the-art deep convolutional neural network (CNN). Unlike traditional CNNs, DenseNet connects each layer to every other layer in a feed-forward fashion. This architecture has several key advantages:</p>
        <ul>
            <li><strong>Strong Gradient Flow:</strong> It alleviates the vanishing gradient problem, allowing for deeper and more accurate models.</li>
            <li><strong>Parameter Efficiency:</strong> It encourages feature reuse, leading to a smaller model size without sacrificing performance.</li>
            <li><strong>Implicit Deep Supervision:</strong> Shorter connections between layers mean that the loss function can more easily influence all layers of the network.</li>
        </ul>
        <p>Our model has been pre-trained on the extensive ImageNet dataset and fine-tuned on a large dataset of chest radiographs to specialize in detecting thoracic pathologies.</p>
    </div>
    <div class='card'>
        <h4>🔍 The Explanation: Grad-CAM</h4>
        <p>Understanding *why* an AI makes a certain decision is crucial, especially in medicine. We use **Gradient-weighted Class Activation Mapping (Grad-CAM)** to provide this transparency.</p>
        <p>Grad-CAM works by analyzing the gradients flowing into the final convolutional layer of our DenseNet model. It produces a coarse localization map that highlights the most important regions in the image for predicting a specific concept (like "Pneumonia").</p>
        <p>In simple terms, it creates a **heatmap** that answers the question: <strong>"Where did the AI look to make its decision?"</strong> This is a cornerstone of Explainable AI (XAI) and helps build trust and interpretability in our results.</p>
    </div>
    """, unsafe_allow_html=True)

def render_faq_page():
    """Renders the FAQ & Disclaimer page."""
    st.markdown("<div class='card-title'>Frequently Asked Questions & Disclaimer</div>", unsafe_allow_html=True)

    with st.expander("Is this tool a replacement for a radiologist?"):
        st.error("**Absolutely not.** This tool is designed as a supplementary aid for educational and informational purposes. It can help highlight potential areas of concern, but it is not a diagnostic tool. All findings must be reviewed and confirmed by a qualified medical professional.")
    
    with st.expander("What image formats are supported?"):
        st.write("The uploader accepts standard image formats, including PNG, JPG, and JPEG. For best results, use high-resolution images.")
        
    with st.expander("How are the confidence scores interpreted?"):
        st.write("A confidence score represents the model's certainty (from 0% to 100%) that a specific feature or pathology is present in the image. A high score does not confirm a diagnosis but indicates a high probability according to the model's training. We flag any finding above 50% for review.")

    with st.expander("Is my data private and secure?"):
        st.write("Yes. Images are processed in a temporary, secure environment and are deleted immediately after the analysis is complete. We do not store any patient data or uploaded images.")
    
    st.markdown(
        """
        <div class='card' style='background-color: #FDEDEC;'>
            <h4 style='color: #C0392B;'>🚨 Important Medical Disclaimer</h4>
            <p>This software is provided "as is" and is intended for informational and research purposes only. It is not intended for use in the diagnosis of disease or other conditions, or in the cure, mitigation, treatment, or prevention of disease. The output of this tool should not be used as the sole basis for clinical decision-making. A licensed physician should be consulted for diagnosis and treatment of any and all medical conditions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =================================================================================================
# --- MAIN APP ROUTER ---
# =================================================================================================

# --- HEADER ---
st.markdown("<p class='main-header'>🩺 Med-AI Advanced X-Ray Analyzer</p>", unsafe_allow_html=True)
st.markdown("<p class='main-subheader'>Leveraging Deep Learning for Insights into Thoracic Pathologies</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- NAVIGATION ---
pages = {
    "🔬 AI Analyzer": render_analyzer_page,
    "💡 About the Technology": render_about_page,
    "❓ FAQ & Disclaimer": render_faq_page,
}

# Use radio buttons in the sidebar for navigation
with st.sidebar:
    st.markdown("<p class='sidebar-header' style='margin-bottom: 20px;'>Navigation</p>", unsafe_allow_html=True)
    selection = st.radio("Go to", list(pages.keys()), label_visibility="collapsed")

# Call the function corresponding to the user's selection
page_function = pages[selection]
page_function()

# --- SIDEBAR FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("Developed with ❤️ using Streamlit & PyTorch.")