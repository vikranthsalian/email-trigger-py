import os
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import smtplib
from email.message import EmailMessage

app = FastAPI()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
