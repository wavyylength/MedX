import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import torch

from model import load_model
from analyze import get_predictions_for_api

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app) # Enable Cross-Origin Resource Sharing
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("--- CXR-Vision AI API Server is starting up ---")
model = load_model()
print("--- Model loaded successfully ---")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filepath = None
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            predictions, heatmaps = get_predictions_for_api(filepath, model)
            if predictions is None:
                 return jsonify({"error": "Could not process image"}), 500
            
            return jsonify({ "predictions": predictions, "heatmaps": heatmaps })
        except Exception as e:
            return jsonify({"error": f"An internal error occurred: {e}"}), 500
        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    print("--- Starting Flask API server at http://127.0.0.1:5000 ---")
    app.run(host='0.0.0.0', port=5000, debug=False)