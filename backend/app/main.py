from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="MedX Explainable AI")

# Healthcheck endpoint
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Predict endpoint (dummy for now)
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Ensure 'static' directory exists
        os.makedirs("static", exist_ok=True)

        temp_path = os.path.join("static", file.filename)

        # Save uploaded file
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        # TODO: Call your ML model here with temp_path
        # prediction = model.predict(temp_path)

        return JSONResponse(content={"message": f"File saved to {temp_path}"})
    except Exception as e:
        print("Error in predict:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

# History endpoint
@app.get("/history/{patient_id}")
async def history(patient_id: str):
    # Dummy history
    data = {
        "patient_id": patient_id,
        "previous_scans": ["scan1.png", "scan2.png"],
        "notes": "No critical findings"
    }
    return JSONResponse(content=data)
