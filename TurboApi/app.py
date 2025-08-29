import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from ultralytics import YOLO
import torch

# --- Load YOLO model on CPU ---
model_path = "model/yolov8_classify_stanford_data.pt"
model = YOLO(model_path).to("cpu")  # CPU-only

app = FastAPI(title="Car Classification YOLO API (CPU)")

@app.get("/")
def read_root():
    return {"message": "YOLO Car Classification API is running. POST an image to /predict."}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Run YOLO inference on CPU
        results = model.predict(image, device="cpu")

        # Extract top classification prediction
        probs = results[0].probs
        top_idx = int(probs.top1)
        confidence = float(probs.top1conf)
        class_name = results[0].names[top_idx]

        return JSONResponse({
            "class": class_name,
            "confidence": confidence,
            "class_id": top_idx
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
