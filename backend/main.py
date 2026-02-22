"""
FastAPI backend for the personal portfolio contact form.

This module defines a simple API endpoint that accepts contact form
submissions and sends them as an email via the Resend service. All
configuration (Resend API key, sender and recipient addresses) is
provided via environment variables, so no secrets are committed in
source control. The endpoint performs basic validation on the name,
email and message fields before sending the email and returns a
JSON object indicating success or failure.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import resend

# Load configuration from environment variables. These values should be
# defined in your Render (or other hosting) service settings. See the
# Render documentation for how to add environment variables.
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# Assign the API key to the Resend SDK. If the key is missing, the
# Resend client will raise an exception when attempting to send mail.
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
    allow_methods=["POST"],
    allow_headers=["*"],
)

class ContactPayload(BaseModel):
    """Schema for incoming contact form submissions."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=1, max_length=500)


@app.post("/api/contact")
def contact(payload: ContactPayload):
    """
    Receive contact form submissions and forward them as an email via Resend.

    The `payload` is validated by Pydantic to ensure the presence and
    correctness of the fields. If successful, an email is sent using
    the Resend API and a JSON response with `ok: true` is returned.
    If sending fails, this endpoint returns a 500 status code with the
    error message.
    """
    # Determine who the email should be sent to. Default to the
    # maintainer's address if not provided via environment.
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
        # Log the exception details and return an error response.
        # In production, consider logging this to an external service.
        raise HTTPException(status_code=500, detail=f"Email failed to send: {exc}")