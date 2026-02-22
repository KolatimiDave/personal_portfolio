"""
Backend for the contact form
===========================

This FastAPI application exposes a single endpoint `/api/contact` that
receives JSON payloads from the portfolio's contact form.  On receiving
the payload, it validates the data, then sends an email via the Resend
API using the provided API key.  The email is addressed to David's
inbox with the visitor's details included and sets `reply_to` so
David can respond directly to the sender.

To run this server locally, install the dependencies and start the
server with uvicorn:

```
pip install fastapi uvicorn resend pydantic[email]
uvicorn main:app --host 0.0.0.0 --port 8000
```

Replace the API key below with your real Resend API key.  For security,
you can also load it from an environment variable instead of hardcoding.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware
import resend

# Replace this with your real Resend API key provided by the user.
resend.api_key = "re_JGsiTNwe_NkKkyKYsgeFmXfatkPCAGJYG"


app = FastAPI()

# Allow requests from any origin; adjust in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)


class ContactPayload(BaseModel):
    """Schema for validating the contact form payload."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=500)


@app.post("/api/contact")
def contact(payload: ContactPayload):
    """Handle incoming contact form submissions and send via Resend."""
    try:
        # Compose the email HTML body
        html_body = f"""
            <h2>New Contact Form Message</h2>
            <p><strong>Name:</strong> {payload.name}</p>
            <p><strong>Email:</strong> {payload.email}</p>
            <p><strong>Message:</strong></p>
            <p>{payload.message}</p>
        """
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": "davidkolatimi@gmail.com",
            "subject": f"New contact form message from {payload.name}",
            "reply_to": payload.email,
            "html": html_body
        })
        return {"ok": True}
    except Exception as exc:
        # Log the exception and return a 500 error
        raise HTTPException(status_code=500, detail="Email failed to send")