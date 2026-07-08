import base64
from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from pypdf import PdfReader, PdfWriter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def generate_pdf(report, prediction, original_image, heatmap, password):

    buffer = BytesIO()
    
    # Decode original image
    original_bytes = base64.b64decode(
        original_image.split(",")[1]
    )

    original_buffer = BytesIO(original_bytes)

    # Decode GradCAM image
    heatmap_bytes = base64.b64decode(
        heatmap
    )

    heatmap_buffer = BytesIO(heatmap_bytes)

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]
    normal = styles["BodyText"]

    story = []

    story.append(Paragraph("MedScan AI Report", title))
    story.append(Spacer(1,20))
    
    story.append(Paragraph("Chest X-ray Images", heading))

    table = Table([
        [
            Image(original_buffer, width=2.8*inch, height=2.8*inch),
            Image(heatmap_buffer, width=2.8*inch, height=2.8*inch)
        ],
        [
            Paragraph("<b>Original X-ray</b>", normal),
            Paragraph("<b>Grad-CAM Heatmap</b>", normal)
        ]
    ])

    table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))

    story.append(table)

    story.append(Spacer(1,20))
    

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            normal
        )
    )

    story.append(Spacer(1,20))

    story.append(Paragraph("<b>Prediction</b>", heading))
    story.append(
        Paragraph(
            prediction["predicted_class"],
            normal
        )
    )

    story.append(
        Paragraph(
            f"Confidence: {prediction['confidence']:.2f}%",
            normal
        )
    )

    story.append(Spacer(1,20))

    story.append(Paragraph("Findings", heading))
    story.append(
        Paragraph(report["findings"], normal)
    )

    story.append(Spacer(1,10))

    story.append(Paragraph("Impression", heading))
    story.append(
        Paragraph(report["impression"], normal)
    )

    story.append(Spacer(1,10))

    story.append(Paragraph("Recommendation", heading))
    story.append(
        Paragraph(report["recommendation"], normal)
    )

    story.append(Spacer(1,25))

    story.append(
        Paragraph(
            "<b>Disclaimer</b><br/>"
            "This report is AI-generated and intended for screening support only."
            " It is not a medical diagnosis.",
            normal
        )
    )

    doc.build(story)

    buffer.seek(0)
    reader = PdfReader(buffer)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)
    encrypted_buffer = BytesIO()
    writer.write(encrypted_buffer)
    encrypted_buffer.seek(0)
    return encrypted_buffer