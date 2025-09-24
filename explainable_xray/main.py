from src.analyze import analyze_image

image_path = r"C:\Users\Prince Kumar\Desktop\hackathon\explainable_xray\data\x3.jpeg"
results = analyze_image(image_path)
print("Predictions:", results)
