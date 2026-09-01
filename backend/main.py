"""
FastAPI backend for the personal portfolio contact form.

This module defines a simple API endpoint that accepts contact form
submissions and sends them as an email via the Resend service. All
configuration (Resend API key, sender and recipient addresses) is
provided via environment variables, so no secrets are committed in
source control.

Also includes a simple /health endpoint for Render health checks.
"""

import logging
import os
import time
from collections import defaultdict, deque
from html import escape

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import resend

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "900"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "5"))

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

app = FastAPI()
logger = logging.getLogger(__name__)

FRONTEND_URLS = [
    "https://david-olukolatimi.onrender.com",
    "https://davidolukolatimi.cv",
    "https://davidolukolatimi.com",
    "https://www.davidolukolatimi.com",
]
CONTACT_ATTEMPTS: defaultdict[str, deque[float]] = defaultdict(deque)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class ContactPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=1, max_length=500)


def get_client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(client_key: str) -> None:
    now = time.time()
    attempts = CONTACT_ATTEMPTS[client_key]

    while attempts and now - attempts[0] > RATE_LIMIT_WINDOW_SECONDS:
        attempts.popleft()

    if len(attempts) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many contact attempts. Please try again later.",
        )

    attempts.append(now)

@app.get("/health")
def health():
    """
    Simple health check endpoint for Render and monitoring.
    Returns minimal info without exposing secrets.
    """
    return {
        "ok": True,
        "status": "healthy",
        "has_resend_key": bool(RESEND_API_KEY),
        "has_to_email": bool(TO_EMAIL),
        "has_from_email": bool(FROM_EMAIL),
    }

@app.post("/api/contact")
def contact(payload: ContactPayload, request: Request):
    enforce_rate_limit(get_client_key(request))

    if not RESEND_API_KEY:
        logger.error("Missing RESEND_API_KEY in environment variables.")
        raise HTTPException(status_code=500, detail="Contact service is not configured.")
    if not TO_EMAIL:
        logger.error("Missing TO_EMAIL in environment variables.")
        raise HTTPException(status_code=500, detail="Contact service is not configured.")
    if not FROM_EMAIL:
        logger.error("Missing FROM_EMAIL in environment variables.")
        raise HTTPException(status_code=500, detail="Contact service is not configured.")

    recipient = TO_EMAIL
    sender = FROM_EMAIL
    safe_name = escape(payload.name)
    safe_email = escape(str(payload.email))
    safe_message = escape(payload.message).replace("\n", "<br>")

    try:
        resend.Emails.send(
            {
                "from": sender,
                "to": [recipient],
                "subject": f"New contact form message from {payload.name[:80]}",
                "reply_to": str(payload.email),
                "html": f"""
                    <h2>New Contact Form Message</h2>
                    <p><strong>Name:</strong> {safe_name}</p>
                    <p><strong>Email:</strong> {safe_email}</p>
                    <p><strong>Message:</strong></p>
                    <p>{safe_message}</p>
                """,
            }
        )
        return {"ok": True}
    except Exception as exc:
        logger.exception("Email failed to send: %s", exc)
        raise HTTPException(status_code=500, detail="Email failed to send. Please try again later.")
