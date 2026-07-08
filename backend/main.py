import io
import base64
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
from pdf_report import generate_pdf

from inference import predict
from gradcam   import generate_heatmap_overlay
from report    import generate_report

app = FastAPI(title="MedScan API")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", frontend_url],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def health_check():
    return {"status": "MedScan API is running"}


@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are accepted."
        )

    contents = await file.read()
    image    = Image.open(io.BytesIO(contents))

    # Run prediction
    prediction = predict(image)

    # Generate GradCAM — now returns (overlay_image, region_description)
    heatmap_image, gradcam_description = generate_heatmap_overlay(image)

    # Convert PIL Image to base64
    buffer = io.BytesIO()
    heatmap_image.save(buffer, format="PNG")
    heatmap_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Generate report — pass both prediction AND gradcam description
    report_sections = generate_report(prediction, gradcam_description)
    # report_sections = {
    #     "findings": "Report generation temporarily disabled.",
    #     "impression": "Report generation temporarily disabled.",
    #     "recommendation": "Report generation temporarily disabled."
    # }

    return JSONResponse({
        "prediction":   prediction,
        "heatmap":      heatmap_b64,
        "report":       report_sections,   # now a dict, not a string
        "gradcam_note": gradcam_description
    })
    
@app.post("/download-report")
async def download_report(data: dict):

    pdf = generate_pdf(
        report=data["report"],
        prediction=data["prediction"],
        original_image=data["original_image"],
        heatmap=data["heatmap"],
        password=data["password"]
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=MedScan_Report.pdf"
        }
    )
