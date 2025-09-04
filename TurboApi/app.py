import torch
import timm
from torchvision import transforms
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

# -----------------------------
# Configuration
# -----------------------------
MODEL_NAME = "swin_large_patch4_window7_224"
CHECKPOINT_PATH = "/app/model/swin_car_model_with_classes.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Chargement du modèle + mapping
# -----------------------------
checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu")

num_classes = len(checkpoint["class_to_idx"])
model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=num_classes)
model.load_state_dict(checkpoint["model_state"])
model.to(DEVICE)
model.eval()

# Mapping idx -> nom de classe
class_to_idx = checkpoint["class_to_idx"]
idx_to_class = {v: k for k, v in class_to_idx.items()}

# -----------------------------
# Prétraitement image
# -----------------------------
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def predict(image: Image.Image, topk: int = 5):
    image = image.convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_idx = torch.topk(probs, topk)

    results = []
    for i in range(topk):
        idx = top_idx[0][i].item()
        prob = top_prob[0][i].item()
        class_name = idx_to_class.get(idx, str(idx))
        results.append({
            "class_id": idx,
            "class_name": class_name,
            "probability": prob
        })
    return results

# -----------------------------
# FastAPI server
# -----------------------------
app = FastAPI()

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    image = Image.open(file.file)
    results = predict(image, topk=5)
    return JSONResponse({"top5_predictions": results})
