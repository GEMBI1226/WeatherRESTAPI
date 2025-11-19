import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import settings

def send_email(subject: str, message: str):
    email_user = settings.email_user
    email_pass = settings.email_pass
    email_to = settings.email_to

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = email_to
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_user, email_pass)
        server.sendmail(email_user, email_to, msg.as_string())
