# FastAPI Email Sender

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Framework-009688)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI%20Server-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
[![Update Traffic Stats](https://github.com/vikranthsalian/email-trigger-py/actions/workflows/update-traffic.yml/badge.svg)](https://github.com/vikranthsalian/email-trigger-py/actions/workflows/update-traffic.yml)
![Repo Visitors](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/vikranthsalian/email-trigger-py&title=Repo%20Visitors)

### Traffic Stats

- Views (last 14 days): <!-- VIEWS_14D -->240<!-- VIEWS_14D -->
- Unique visitors (last 14 days): <!-- UNIQUES_14D -->3<!-- UNIQUES_14D -->


This repository contains a small FastAPI application that accepts form-data (including file attachments) and sends emails using SMTP. It also includes a `/check-smtp` endpoint to test TCP connectivity to an SMTP server.

---

## Files

* `main.py` — Main FastAPI application with two endpoints:

  * `POST /check-smtp` — TCP connectivity check (JSON body: `host`, `port`, `timeout`).
  * `POST /send-email` — Sends an email with optional attachments. Form fields: `to`, `subject`, `message`, `smtp_user`, `smtp_password`, and one or more `files`.

---

## Requirements

Create a `requirements.txt` with the following contents:

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.9
```

If you plan to use the SendGrid alternative (recommended on platforms that block SMTP), add:

```
requests==2.31.0
```

---

## Local development

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate  # Windows (PowerShell/CMD)
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
export PORT=8000    # optional
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
```

4. Test endpoints:

* `/check-smtp` (POST JSON):

```json
{
  "host": "smtp.gmail.com",
  "port": 587,
  "timeout": 5
}
```

* `/send-email` (POST form-data): keys `to`, `subject`, `message`, `smtp_user`, `smtp_password`, and `files` (set type `File` in Postman). The endpoint will attempt to connect to the configured SMTP host (`smtp.gmail.com:587` by default) and send the message.

---

## Deploying to Render.com

1. Push your project to a Git repository (GitHub/GitLab/Bitbucket).
2. Create a new **Web Service** on Render and link the repository.
3. Use the following **Start Command**:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. Ensure `requirements.txt` is present so Render installs dependencies.

> **Important:** Many Render plans (especially free instances) block outbound SMTP ports (25, 465, 587). If you see `OSError: [Errno 101] Network is unreachable` or a connection failure on `/check-smtp`, Render is likely blocking SMTP. See the Troubleshooting section below.

---

## Environment & Security

* This implementation accepts SMTP credentials via form fields (`smtp_user`, `smtp_password`) for flexibility/testing. **Do not** log or store plaintext credentials in production.
* For production, prefer using secure environment variables or a secrets manager provided by your hosting platform.
* If you use provider APIs (SendGrid, Mailgun, SES), set API keys as Render environment variables.

---

## Troubleshooting & Alternatives

* **Network is unreachable on Render**: Render often blocks outbound SMTP — use an HTTPS-based email API (SendGrid, Mailgun, Postmark, Amazon SES) instead. This avoids SMTP port restrictions and is more reliable for hosted platforms.

* **Gmail-specific notes**: If using Gmail SMTP, use an **app password** (if your account has 2FA) or configure OAuth2. Regular account password logins are often blocked or disabled.

* **Debugging**: Temporarily enable SMTP debug by setting `DEBUG_SMTP=1` in your environment and inspect logs. Also use `/check-smtp` to confirm connectivity.

---

## Postman

I recommend creating a Postman collection with two requests:

1. `Check SMTP` — POST `{{BASE_URL}}/check-smtp` with JSON body `{ "host": "smtp.gmail.com", "port": 587, "timeout": 5 }`.
2. `Send Email` — POST `{{BASE_URL}}/send-email` with **form-data** for `to`, `subject`, `message`, `smtp_user`, `smtp_password`, and `files` (type: File). Duplicate `files` keys to send multiple attachments.

---

## SendGrid Alternative Example (short)

If Render blocks SMTP, switch to an API provider. Add `requests` to `requirements.txt` and implement a handler that uploads attachments as base64 and calls SendGrid's `/v3/mail/send`. This uses HTTPS and works from Render.

---

## License

MIT

---

If you want I can:

* Add a ready-to-import Postman collection and environment file.
* Replace the `send-email` handler with a SendGrid implementation and provide updated `requirements.txt`.
* Add a `Dockerfile` or `render.yaml` for automatic deploy.

Tell me which of these you'd like next.
