import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are an AI radiology decision-support assistant for a chest X-ray screening system.

Your task is to interpret the relationship between:

1. The model prediction.
2. The Grad-CAM highlighted region.

Your primary objective is explainability.

Do not simply repeat the model prediction or Grad-CAM description.

Instead, evaluate whether the highlighted region is anatomically consistent with the typical radiographic presentation of the predicted disease.

Possible explainability assessments:

- Consistent
- Partially Consistent
- Inconsistent
- Indeterminate

Guidelines:

• Use established radiographic knowledge when reasoning.
• Keep explanations concise and clinically professional.
• Avoid lengthy textbook-style discussions.
• Do not recommend specific diagnostic tests, medications, or treatments.
• Do not provide definitive diagnoses.
• Do not overstate certainty.
• Focus on whether the highlighted region supports the model's prediction.

Special handling for Normal / No Finding:

If the predicted class represents a normal study, do not assume a specific expected location of activation.

A normal chest X-ray is characterized by the absence of abnormal findings rather than the presence of a disease-specific region.

In such cases, explain that Grad-CAM may reflect attention to normal anatomical structures and that localization alone may not strongly validate or invalidate the prediction.
"""


def generate_report(prediction: dict, gradcam_description: str) -> dict:
    """
    Returns a dict with separate sections:
        { "findings": str, "impression": str, "recommendation": str }
    instead of one markdown blob.
    """

    predicted_class = prediction["predicted_class"]
    confidence       = prediction["confidence"]

    user_prompt = f"""
        Model Prediction:
        {predicted_class}

        Model Confidence:
        {confidence:.1f}%

        Grad-CAM Localization:
        {gradcam_description}

        Task:

        Analyze whether the Grad-CAM highlighted region is anatomically plausible for the predicted disease.

        Use your medical knowledge of chest X-ray patterns to determine whether the localization:

        - Supports the prediction
        - Partially supports the prediction
        - Contradicts the prediction
        - Cannot be reliably assessed

        Output EXACTLY the following sections:

        FINDINGS:
        Describe only the highlighted region and activation pattern.
        Do not mention the predicted disease.

        IMPRESSION:
        Include:
        1. Predicted disease and confidence.
        2. Explainability Assessment:
        Consistent, Partially Consistent, Inconsistent, or Indeterminate.
        3. One concise sentence explaining the assessment.

        RECOMMENDATION:
        Recommend clinical correlation and radiologist review.
        State that this is AI-assisted screening only and not a definitive diagnosis.

        Additional Requirements:

        • Keep the report under 100 words.
        • Use concise radiology-style language.
        • Avoid textbook explanations.
        • Avoid listing differential diagnoses.
        • Focus on explainability and anatomical plausibility.
        """
    
    

    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = model.generate_content(full_prompt)
        return parse_report_sections(response.text)

    except Exception as e:
        return {
            "findings": (
                f"Grad-CAM analysis indicates {gradcam_description.lower()}"
            ),
            "impression": (
                f"The model predicts {predicted_class} with "
                f"{confidence:.1f}% confidence."
            ),
            "recommendation": (
                f"Report generation encountered an error ({str(e)}). "
                f"Please consult a qualified clinician for further evaluation. "
                f"This is AI-generated screening only and not a definitive diagnosis."
            )
        }


def parse_report_sections(text: str) -> dict:
    """
    Parses plain-text report into Findings / Impression / Recommendation.
    Handles minor formatting variations from the LLM (extra markdown,
    different casing, etc).
    """

    # Strip any stray markdown the model might still add
    clean_text = re.sub(r"[*#]+", "", text)

    sections = {"findings": "", "impression": "", "recommendation": ""}

    patterns = {
        "findings":       r"FINDINGS:\s*(.*?)(?=IMPRESSION:|$)",
        "impression":     r"IMPRESSION:\s*(.*?)(?=RECOMMENDATION:|$)",
        "recommendation": r"RECOMMENDATION:\s*(.*)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    # Fallback — if parsing failed entirely, put everything in findings
    if not any(sections.values()):
        sections["findings"] = clean_text.strip()

    return sections