# tests/test_main.py
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app

client = TestClient(app)


def test_check_smtp_success(monkeypatch):
    """check_smtp should return ok=True when socket.create_connection works."""

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    def fake_create_connection(addr, timeout=5.0):
        # Just return a dummy context manager; no real network call.
        return DummySocket()

    # Patch socket.create_connection used in main.py
    monkeypatch.setattr("main.socket.create_connection", fake_create_connection)

    resp = client.post(
        "/check-smtp",
        json={"host": "smtp.gmail.com", "port": 587, "timeout": 1.0},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["host"] == "smtp.gmail.com"
    assert data["port"] == 587


def test_check_smtp_failure(monkeypatch):
    """check_smtp should raise HTTPException when socket.create_connection fails."""

    def fake_create_connection(addr, timeout=5.0):
        raise OSError("Unable to connect")

    monkeypatch.setattr("main.socket.create_connection", fake_create_connection)

    resp = client.post(
        "/check-smtp",
        json={"host": "invalid.host", "port": 9999, "timeout": 1.0},
    )

    assert resp.status_code == 502
    body = resp.json()
    assert "Connection failed" in body["detail"]


@patch("main.smtplib.SMTP")
@patch("main.smtplib.SMTP_SSL")
def test_send_email_success(mock_smtp_ssl, mock_smtp):
    """
    send_email should:
    - create an EmailMessage
    - call login and send_message on SMTP
    - return 200 with message_id and attachments
    We mock SMTP so no real email is sent.
    """

    # Configure the mock for the non-SSL SMTP (port 587 in your code)
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value = mock_smtp_instance

    # We don't expect SMTP_SSL to be used for port 587, but it's patched anyway
    mock_smtp_ssl_instance = MagicMock()
    mock_smtp_ssl.return_value = mock_smtp_ssl_instance

    # Prepare form data + a fake file
    data = {
        "to": "vikkysalian@gmail.com",
        "subject": "Test subject",
        "message": "Hello from test!",
        "smtp_user": "primedroidomega@gmail.com",
        "smtp_password": "bpes yhgw cvff huge",
    }

    files = {
        # field name must match `files: List[UploadFile] = File(default=[])`
        # (FastAPI will treat multiple "files" fields as the list)
        "files": ("test.txt", b"hello world", "text/plain")
    }

    resp = client.post("/send-email", data=data, files=files)

    assert resp.status_code == 200
    body = resp.json()

    assert body["status"] == "Email sent"
    assert "message_id" in body
    assert body["attachments"] == ["test.txt"]

    # Verify SMTP was used
    mock_smtp.assert_called_once()  # SMTP (not SMTP_SSL) for port 587
    assert mock_smtp_instance.login.called, "SMTP login should be called"
    assert mock_smtp_instance.send_message.called, "send_message should be called"
    assert mock_smtp_instance.quit.called, "quit should be called"


def test_send_email_missing_form_field():
    """
    FastAPI should return 422 if required form fields are missing.
    e.g., smtp_user or smtp_password not provided.
    """

    resp = client.post(
        "/send-email",
        data={
            "to": "receiver@example.com",
            "subject": "No creds",
            "message": "This should fail because creds are missing",
            # intentionally not sending smtp_user / smtp_password
        },
    )

    # FastAPI validation error (Unprocessable Entity)
    assert resp.status_code == 422
