"""Email notification tool using Resend API (direct HTTP for UTF-8 support)."""

import httpx
from config import settings

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email via Resend HTTP API.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text (will be wrapped in HTML).

    Returns:
        dict with success status and message/error.
    """
    # Convert plain text body to simple HTML
    html_body = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;
                padding: 24px; color: #1a1a2e; line-height: 1.6;">
        <div style="border-bottom: 3px solid #6c63ff; padding-bottom: 16px; margin-bottom: 24px;">
            <h2 style="margin: 0; color: #6c63ff;">Career Agent Response</h2>
            <p style="margin: 4px 0 0; color: #888; font-size: 14px;">
                Automated response from Deniz Buyuksahin's Career Assistant
            </p>
        </div>
        <div style="white-space: pre-wrap; font-size: 15px;">
{body}
        </div>
        <div style="border-top: 1px solid #eee; margin-top: 32px; padding-top: 16px;
                    font-size: 12px; color: #999;">
            This email was composed with the assistance of an AI Career Agent and reviewed
            for quality before sending.
        </div>
    </div>
    """

    payload = {
        "from": settings.FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html_body,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RESEND_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "id": result.get("id", "unknown"),
                }
            else:
                return {
                    "success": False,
                    "error": f"Resend returned status {response.status_code}: {response.text}",
                }
    except Exception as e:
        return {"success": False, "error": str(e)}
