import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import torch

# Import your project's modules
from src.model import load_model
from src.analyze import get_predictions_for_api # This function now returns heatmaps too

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- MODEL LOADING ---
print("--- Med-AI Server is starting up ---")
model = load_model()
print("--- Model loaded successfully ---")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API ROUTES ---

@app.route('/')
def serve_app():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        filepath = None # Define filepath here to be accessible in finally block
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"--- Analyzing image: {filepath} ---")
            
            # This now returns two values: predictions and heatmaps
            predictions, heatmaps = get_predictions_for_api(filepath, model)
            
            if predictions is None:
                 return jsonify({"error": "Could not process image"}), 500
            
            print("--- Analysis complete, sending results and heatmaps. ---")
            # Return both predictions and heatmaps in the response
            return jsonify({
                "predictions": predictions,
                "heatmaps": heatmaps
            })

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": "An internal error occurred during analysis"}), 500
        finally:
            # Clean up the uploaded file
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({"error": "File type not allowed"}), 400

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    print("--- Starting Flask server at http://127.0.0.1:5000 ---")
    app.run(host='0.0.0.0', port=5000, debug=False)