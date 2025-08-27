from flask import Flask, request, jsonify
import torch
from torchvision import transforms
from PIL import Image
import pandas as pd

# --- Device configuration ---
device = torch.device("cpu")  # Force CPU

# --- Load the model ---
try:
    model = torch.jit.load("model/resnet18_turbodex_ts.pt", map_location=device)
    model.eval()
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- Load class names ---
try:
    classes_df = pd.read_csv("classes_compcars.csv")
    class_map = {row['ClassIndex']: row['ClassName'] for _, row in classes_df.iterrows()}
except Exception as e:
    print(f"Error loading class CSV: {e}")
    class_map = {}

# --- Image preprocessing ---
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# --- Flask app ---
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    try:
        img = Image.open(file).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image: {e}"}), 400

    # Preprocess
    input_tensor = preprocess(img).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)

    # Build response
    results = []
    for i in range(top5_prob.size(0)):
        idx = top5_catid[i].item()
        results.append({
            "ClassIndex": idx,
            "ClassName": class_map.get(idx, "Unknown"),
            "Probability": float(top5_prob[i].item())
        })

    return jsonify({"predictions": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
