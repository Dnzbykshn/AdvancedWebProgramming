"""Mobile notification tool using ntfy.sh — free push notification service."""

import httpx
from config import settings

NTFY_BASE_URL = "https://ntfy.sh"


async def send_notification(
    title: str,
    message: str,
    priority: str = "default",
    tags: str = "",
) -> dict:
    """Send a push notification via ntfy.sh.

    Args:
        title: Notification title (ASCII-safe, use tags for emoji).
        message: Notification body text.
        priority: One of 'min', 'low', 'default', 'high', 'urgent'.
        tags: Comma-separated emoji tags (e.g., 'briefcase,email').

    Returns:
        dict with success status and details.
    """
    url = f"{NTFY_BASE_URL}/{settings.NTFY_TOPIC}"

    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": tags,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                content=message.encode("utf-8"),
                headers=headers,
            )
            if response.status_code == 200:
                return {"success": True, "message": "Notification sent successfully"}
            else:
                return {
                    "success": False,
                    "error": f"ntfy returned status {response.status_code}: {response.text}",
                }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def notify_new_message(sender_name: str, subject: str) -> dict:
    """Send notification when a new employer message arrives."""
    return await send_notification(
        title="New Employer Message",
        message=f"From: {sender_name}\nSubject: {subject}",
        priority="high",
        tags="briefcase,incoming_envelope",
    )


async def notify_response_sent(sender_name: str, score: float) -> dict:
    """Send notification when a response is approved and sent."""
    return await send_notification(
        title="Response Sent",
        message=f"Reply sent to {sender_name}\nEvaluation Score: {score}/10",
        priority="default",
        tags="white_check_mark,email",
    )


async def notify_unknown_question(sender_name: str, reason: str) -> dict:
    """Send notification when an unknown question is detected."""
    return await send_notification(
        title="Human Intervention Needed",
        message=f"From: {sender_name}\nReason: {reason}\n\nPlease review and respond manually.",
        priority="urgent",
        tags="warning,question",
    )
