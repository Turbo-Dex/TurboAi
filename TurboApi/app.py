from flask import Flask, request, send_file, jsonify
import torch
from torchvision import transforms
from PIL import Image
import io

# --- Device ---
device = torch.device("cpu")

# --- Load model ---
# Assume blur.pt is a standard PyTorch model (state_dict or full model)
try:
    model = torch.jit.load("model/resnet18_turbodex_ts.pt", map_location=device)
    model.eval()
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- Transform ---
preprocess = transforms.Compose([
    transforms.ToTensor()
])

postprocess = transforms.Compose([
    transforms.ToPILImage()
])

# --- Flask app ---
app = Flask(__name__)

@app.route("/blur", methods=["POST"])
def blur_image():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    try:
        pil_img = Image.open(file).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image: {e}"}), 400

    # Preprocess
    input_tensor = preprocess(pil_img).unsqueeze(0).to(device)

    # Model inference
    with torch.no_grad():
        output_tensor = model(input_tensor)

    # Convert output tensor to PIL image
    output_tensor = output_tensor.squeeze(0).cpu().clamp(0, 1)
    output_img = postprocess(output_tensor)

    # Encode as JPEG
    buf = io.BytesIO()
    output_img.save(buf, format="JPEG")
    buf.seek(0)

    return send_file(buf, mimetype="image/jpeg", as_attachment=False, download_name="blurred.jpg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
