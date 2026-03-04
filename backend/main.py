"""
FastAPI backend for the personal portfolio contact form.

This module defines a simple API endpoint that accepts contact form
submissions and sends them as an email via the Resend service. All
configuration (Resend API key, sender and recipient addresses) is
provided via environment variables, so no secrets are committed in
source control.

Also includes a simple /health endpoint for Render health checks.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import resend

# Load config from environment variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")


# Configure Resend SDK
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

app = FastAPI()

FRONTEND_URLS = [
    "https://david-olukolatimi.onrender.com",
    "https://davidolukolatimi.com",
]

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
def contact(payload: ContactPayload):
    # Validate env vars early with a clear error
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Missing RESEND_API_KEY in environment variables.")
    if not TO_EMAIL:
        raise HTTPException(status_code=500, detail="Missing TO_EMAIL in environment variables.")
    if not FROM_EMAIL:
        raise HTTPException(status_code=500, detail="Missing FROM_EMAIL in environment variables.")

    recipient = TO_EMAIL
    sender = FROM_EMAIL

    try:
        resend.Emails.send(
            {
                "from": sender,
                "to": [recipient],
                "subject": f"New contact form message from {payload.name}",
                "reply_to": payload.email,
                "html": f"""
                    <h2>New Contact Form Message</h2>
                    <p><strong>Name:</strong> {payload.name}</p>
                    <p><strong>Email:</strong> {payload.email}</p>
                    <p><strong>Message:</strong></p>
                    <p>{payload.message}</p>
                """,
            }
        )
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email failed to send: {exc}")