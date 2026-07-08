import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

from model import build_resnet50

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = build_resnet50()
_model.load_state_dict(
    torch.load("models/best_resnet50.pth", map_location=DEVICE)
)
_model.eval()
_model.to(DEVICE)

_target_layer = [_model.layer4[-1]]
_cam = GradCAM(model=_model, target_layers=_target_layer)

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def describe_activation_region(grayscale_cam: np.ndarray) -> str:
    """
    Splits the 224x224 heatmap into a 3x3 grid (top/middle/bottom x
    left/center/right) and returns a human-readable description of
    where the activation is strongest. This is fed to the LLM as the
    "Grad-CAM findings" text.
    """
    h, w = grayscale_cam.shape

    # Define 3x3 grid boundaries
    row_bounds = [0, h // 3, 2 * h // 3, h]
    col_bounds = [0, w // 3, 2 * w // 3, w]

    row_labels = ["upper", "middle", "lower"]
    col_labels = ["left", "central", "right"]

    region_scores = {}

    for r in range(3):
        for c in range(3):
            r0, r1 = row_bounds[r], row_bounds[r + 1]
            c0, c1 = col_bounds[c], col_bounds[c + 1]
            patch = grayscale_cam[r0:r1, c0:c1]
            region_scores[(row_labels[r], col_labels[c])] = float(patch.mean())

    # Sort regions by activation strength, descending
    sorted_regions = sorted(region_scores.items(), key=lambda x: x[1], reverse=True)

    # Take top region, and second region only if it's reasonably close
    top_region, top_score = sorted_regions[0]
    second_region, second_score = sorted_regions[1]

    def region_to_text(region):
        row, col = region
        # "central" combined with row reads better without "central" prefix
        if col == "central":
            return f"{row} lung field"
        return f"{row} {col} lung field"

    if second_score >= top_score * 0.85:
        # Two regions roughly equally activated
        return (
            f"High activation observed in the {region_to_text(top_region)} "
            f"and {region_to_text(second_region)}."
        )
    else:
        return f"High activation observed in the {region_to_text(top_region)}."


def generate_heatmap_overlay(image: Image.Image):
    """
    Takes a PIL Image.
    Returns:
        - overlay_image: PIL Image with heatmap overlaid
        - region_description: text description of activation location
    """
    image_rgb = image.convert("RGB").resize((224, 224))

    input_tensor = _transform(image_rgb).unsqueeze(0).to(DEVICE)

    grayscale_cam = _cam(input_tensor=input_tensor)[0]

    rgb_img = np.array(image_rgb) / 255.0
    rgb_img = rgb_img.astype(np.float32)

    visualization = show_cam_on_image(
        rgb_img,
        grayscale_cam,
        use_rgb=True
    )

    overlay_image = Image.fromarray(visualization)
    region_description = describe_activation_region(grayscale_cam)

    return overlay_image, region_description