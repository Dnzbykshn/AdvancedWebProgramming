"""In-memory conversation history store — tracks messages per employer (by email)."""

from datetime import datetime
from typing import Optional


class ConversationEntry:
    """Single message-response pair in a conversation."""

    def __init__(
        self,
        employer_message: str,
        agent_response: str,
        status: str,
        timestamp: Optional[str] = None,
    ):
        self.employer_message = employer_message
        self.agent_response = agent_response
        self.status = status
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "employer_message": self.employer_message,
            "agent_response": self.agent_response,
            "status": self.status,
            "timestamp": self.timestamp,
        }


class ConversationMemory:
    """In-memory conversation history store, keyed by sender email.

    Tracks all previous interactions with each employer so the Career Agent
    can maintain context continuity across messages.
    """

    def __init__(self):
        self._store: dict[str, list[ConversationEntry]] = {}

    def add_entry(
        self,
        sender_email: str,
        employer_message: str,
        agent_response: str,
        status: str,
    ) -> None:
        """Record a new message-response pair for an employer."""
        if sender_email not in self._store:
            self._store[sender_email] = []

        self._store[sender_email].append(
            ConversationEntry(
                employer_message=employer_message,
                agent_response=agent_response,
                status=status,
            )
        )

    def get_history(self, sender_email: str) -> list[dict]:
        """Get the full conversation history for an employer."""
        if sender_email not in self._store:
            return []
        return [entry.to_dict() for entry in self._store[sender_email]]

    def get_context_prompt(self, sender_email: str) -> str:
        """Build a context string from conversation history for the Career Agent.

        Returns an empty string if there is no prior history.
        """
        history = self._store.get(sender_email, [])
        if not history:
            return ""

        lines = ["## Previous Conversation History with this employer:"]
        for i, entry in enumerate(history, 1):
            lines.append(f"\n### Exchange {i} ({entry.timestamp})")
            lines.append(f"**Employer said:** {entry.employer_message}")
            if entry.agent_response:
                lines.append(f"**You responded:** {entry.agent_response}")
            else:
                lines.append("*(Flagged for human review — no automated response sent)*")
        lines.append(
            "\n**IMPORTANT:** Use this conversation history to maintain continuity. "
            "Reference previous exchanges when appropriate. Avoid repeating yourself."
        )
        return "\n".join(lines)

    def get_all_conversations(self) -> dict:
        """Get all conversations grouped by email."""
        result = {}
        for email, entries in self._store.items():
            result[email] = [e.to_dict() for e in entries]
        return result

    def clear(self) -> None:
        """Clear all conversation history."""
        self._store.clear()


# Singleton instance
memory = ConversationMemory()
