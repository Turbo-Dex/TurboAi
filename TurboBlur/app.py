import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from ultralytics import YOLO
import cv2
import numpy as np

app = FastAPI(title="TurboBlur YOLO API")

# Load YOLO model
model_path = "model/blur.pt"
model = YOLO(model_path)

@app.get("/")
def read_root():
    return {"message": "TurboBlur YOLO API is running. POST an image to /blur."}

@app.post("/blur/")
async def blur_image(file: UploadFile = File(...)):
    # Read uploaded image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)

    # Run YOLO inference
    results = model(img_np)

    # Get the first result
    result = results[0]

    # Apply blurring to detected boxes
    for box in result.boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        roi = img_np[y1:y2, x1:x2]
        blurred = cv2.GaussianBlur(roi, (101, 101), 50)
        img_np[y1:y2, x1:x2] = blurred

    # Convert back to PIL image
    output_image = Image.fromarray(img_np)

    # Save to bytes
    buf = io.BytesIO()
    output_image.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
