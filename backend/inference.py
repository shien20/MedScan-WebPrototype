import os
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from model import build_resnet50

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = ["Normal", "Pneumonia", "COVID-19", "Tuberculosis"]

MODEL_PATH = os.path.join("models", "best_resnet50.pth")


def load_model():
    model = build_resnet50()
    model.load_state_dict(
        torch.load(MODEL_PATH, map_location=DEVICE)
    )
    model.to(DEVICE)
    model.eval()
    return model


MODEL = load_model()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def predict(image: Image.Image) -> dict:
    """
    Takes a PIL Image (not a file path).
    Returns prediction dict with predicted_class, confidence,
    and all_probabilities — all three required by report.py.
    """
    image = image.convert("RGB")

    tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs       = MODEL(tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)

    predicted_class = CLASS_NAMES[predicted_idx.item()]
    confidence_val  = confidence.item() * 100

    # Build all_probabilities dict — required by report.py
    all_probs = {
        CLASS_NAMES[i]: round(probabilities[0][i].item() * 100, 2)
        for i in range(len(CLASS_NAMES))
    }

    return {
        "predicted_class":    predicted_class,       # fix: was "prediction"
        "confidence":         round(confidence_val, 2),
        "all_probabilities":  all_probs               # fix: was missing
    }