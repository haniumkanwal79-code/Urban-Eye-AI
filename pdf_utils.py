from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_pdf(issue_type, location, image_path):

    os.makedirs("reports", exist_ok=True)

    file_name = f"reports/{issue_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    c = canvas.Canvas(file_name)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Urban Issue Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Issue Type: {issue_type}")
    c.drawString(50, 750, f"Location: {location}")
    c.drawString(50, 730, f"Time: {datetime.now()}")

    c.drawString(50, 700, f"Image Path: {image_path}")

    c.drawString(50, 660, "Auto-generated report by Urban AI System")

    c.save()

    return file_name
