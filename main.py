import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"   # or your provider's SMTP server
SMTP_PORT = 587                # 587 for TLS, 465 for SSL
SMTP_USER = "your_email@example.com"
SMTP_PASS = "your_smtp_or_app_password"

def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Connect to SMTP server with TLS
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)  # <-- auth happens here
        server.send_message(msg)

if __name__ == "__main__":
    send_email(
        to_email="receiver@example.com",
        subject="Test email from Python",
        body="Hello! This is a test email sent using Python + SMTP auth."
    )
