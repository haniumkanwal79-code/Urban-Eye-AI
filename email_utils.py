import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_email(subject, body, pdf_path):

    sender_email = "yourgmail@gmail.com"
    sender_password = "your_app_password"
    receiver_email = "receiver@gmail.com"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # TEXT BODY
    msg.attach(MIMEText(body, "plain"))

    # ATTACH PDF
    attachment = open(pdf_path, "rb")

    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename={pdf_path.split('/')[-1]}"
    )

    msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
