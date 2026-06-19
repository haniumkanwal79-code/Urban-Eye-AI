from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def create_pdf(issue_type, location, image_path, timestamp=None):

    file_name = f"report_{datetime.now().timestamp()}.pdf"

    pdf = SimpleDocTemplate(file_name, pagesize=A4)

    styles = getSampleStyleSheet()

    content = [
        Paragraph("Urban AI Report", styles["Title"]),
        Paragraph(f"Issue: {issue_type}", styles["Normal"]),
        Paragraph(f"Location: {location}", styles["Normal"])
    ]

    pdf.build(content)

    return file_name
