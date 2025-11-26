import os
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import smtplib
from email.message import EmailMessage

app = FastAPI()

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

@app.post("/send-email")
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(message)

    for file in files:
        content = await file.read()
        maintype, subtype = "application", "octet-stream"
        if file.content_type and "/" in file.content_type:
            maintype, subtype = file.content_type.split("/", 1)

        msg.add_attachment(
            content,
            maintype=maintype,
            subtype=subtype,
            filename=file.filename,
        )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    return {"status": "Email sent"}
