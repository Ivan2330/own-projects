import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

async def send_email(subject: str, recipient: str, body: str):
    message = MIMEMultipart()
    message["From"] = settings.email_from
    message["To"] = recipient
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_server,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )

