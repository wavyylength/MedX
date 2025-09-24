# Chest X-Ray Pathology Detector with Grad-CAM

This project uses a pre-trained DenseNet-121 model to detect common thoracic pathologies in chest X-ray images and visualizes the results using Grad-CAM heatmaps.

## Setup

1.  **Clone the repository or download the files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Edit `main.py`:**
    Open the `main.py` file and change the `IMAGE_PATH` variable on line 13 to the path of your X-ray image.

    ```python
    # line 13
    IMAGE_PATH = "C:/Users/YourUser/Desktop/chest_xray.png"
    ```

2.  **Run the script from your terminal:**
    ```bash
    python main.py
    ```

The script will then print the analysis results to the console and display plots for the probabilities and Grad-CAM heatmaps.