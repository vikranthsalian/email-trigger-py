# main.py
import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-sender")

# Load from env (set these in your environment / Render secrets)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587")) # 587 for STARTTLS, 465 for SSL
# SMTP_USER = "primedroidomega@gmail.com"
# SMTP_PASS = "bpes yhgw cvff huge"
DEBUG_SMTP = "1"

# Basic validation so we fail fast with a clear message
# if not SMTP_USER or not SMTP_PASS:
#     logger.warning("SMTP_USER or SMTP_PASS environment variable is not set. "
#                    "Set them before running. Current values: "
#                    f"SMTP_USER={'set' if SMTP_USER else 'NOT SET'}, SMTP_PASS={'set' if SMTP_PASS else 'NOT SET'}")


@app.post("/send-email")
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    smtp_user: str = Form(...),
    smtp_password: str = Form(...)
):
    # Validate env before even trying to connect
    if not smtp_user or not smtp_password:
        raise HTTPException(status_code=500, detail="SMTP credentials are not configured on the server. "
                                                    "Set SMTP_USER and SMTP_PASS environment variables.")

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(message)

    # optionally add a simple HTML part too
    msg.add_alternative(f"<html><body><p>{message}</p></body></html>", subtype="html")

    # Attach files if provided
    for file in files:
        content = await file.read()
        maintype, subtype = "application", "octet-stream"
        try:
            if file.content_type and "/" in file.content_type:
                maintype, subtype = file.content_type.split("/", 1)
        except Exception:
            pass
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=file.filename)

    # Unique message-id for debugging/tracking
    msg_id = make_msgid()
    msg["Message-ID"] = msg_id
    logger.info(f"Preparing to send message {msg_id} to {to} with {len(files)} attachments")

    try:
        # For port 587: connect, starttls, then login
        if SMTP_PORT == 465:
            # SSL connection (port 465)
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)

        # optional detailed logging of the SMTP session
        if DEBUG_SMTP:
            server.set_debuglevel(1)

        # If not SSL, use STARTTLS
        if SMTP_PORT != 465:
            server.ehlo()
            server.starttls()
            server.ehlo()

        # Attempt login
        if isinstance(SMTP_USER, str) and isinstance(SMTP_PASS, str):
            # explicit check to avoid None causing smtplib internal errors
            server.login(smtp_user, smtp_password)
        else:
            raise HTTPException(status_code=500, detail="SMTP_USER or SMTP_PASS is not a string.")

        # Send message
        server.send_message(msg)
        logger.info(f"Email {msg_id} sent successfully to {to}")

    except smtplib.SMTPAuthenticationError as e:
        # 5xx auth error; return readable message and log server response
        logger.error("SMTPAuthenticationError: %s", e)
        # e.smtp_code and e.smtp_error available
        raise HTTPException(status_code=400, detail=f"Authentication failed: {getattr(e, 'smtp_error', e)}")
    except smtplib.SMTPResponseException as e:
        logger.error("SMTPResponseException: code=%s, msg=%s", getattr(e, "smtp_code", None), getattr(e, "smtp_error", e))
        raise HTTPException(status_code=502, detail=f"SMTP server responded with code {getattr(e, 'smtp_code', e)}: {getattr(e, 'smtp_error', e)}")
    except Exception as e:
        logger.exception("Unexpected error while sending email")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        try:
            server.quit()
        except Exception:
            # best-effort close
            pass

    return {"status": "Email sent", "message_id": msg_id, "attachments": [f.filename for f in files]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
