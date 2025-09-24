# Import the functions from our other modules
from model import load_model
from analyze import analyze_xray

# ===================================================================
#                          CONFIGURATION
# ===================================================================

# 📌
# 📌 ===> REPLACE THIS WITH THE PATH TO YOUR X-RAY IMAGE <===
# 📌
IMAGE_PATH = r"C:\Users\Prince Kumar\Desktop\hackathon\MedX\explainable_xray\data\x3.jpeg"


# ===================================================================
#                           RUN ANALYSIS
# ===================================================================

def main():
    """The main function to run the script."""
    # Check if the placeholder path is still being used
    if "path/to/your" in IMAGE_PATH:
        print("=" * 60)
        print("🚨 ACTION REQUIRED 🚨")
        print("\nPlease edit 'main.py' and update the 'IMAGE_PATH' variable on line 13")
        print("with the actual file path to your chest X-ray image.")
        print("=" * 60)
        return
    
    # Load the model and run the analysis
    model = load_model()
    analyze_xray(IMAGE_PATH, model)


if __name__ == "__main__":
    main()