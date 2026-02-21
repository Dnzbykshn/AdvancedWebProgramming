"""Pydantic request/response schemas for the API."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmployerMessage(BaseModel):
    """Incoming message from a potential employer."""

    sender_name: str = Field(..., description="Name of the employer/recruiter")
    sender_email: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Email subject line")
    message: str = Field(..., description="Full message body from the employer")


class EvaluationDetail(BaseModel):
    """Detailed evaluation scores from the evaluator agent."""

    tone_score: int = 0
    clarity_score: int = 0
    completeness_score: int = 0
    safety_score: int = 0
    relevance_score: int = 0
    overall_score: float = 0.0
    feedback: str = ""
    approved: bool = False


class ConfidenceDetail(BaseModel):
    """Unknown detector confidence information."""

    confidence: float = Field(0.0, description="Confidence score 0.0–1.0")
    category: str = Field("safe", description="Detection category")
    reason: str = Field("", description="Reason for the classification")
    is_unknown: bool = False


class AgentResponse(BaseModel):
    """Full response from the career agent pipeline."""

    status: str = Field(..., description="'approved', 'flagged_unknown', or 'error'")
    response_text: str = Field(default="", description="Final generated response")
    evaluation: Optional[EvaluationDetail] = None
    revision_count: int = 0
    unknown_detection: Optional[dict] = None
    confidence: Optional[ConfidenceDetail] = None
    email_result: Optional[dict] = None
    notification_result: Optional[dict] = None
    conversation_history: Optional[list] = None
    error: Optional[str] = None


class EvaluationLog(BaseModel):
    """Single evaluation log entry."""

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    sender_name: str = ""
    sender_email: str = ""
    subject: str = ""
    employer_message: str = ""
    response_text: str = ""
    evaluation: Optional[EvaluationDetail] = None
    revision_count: int = 0
    status: str = ""
    unknown_detection: Optional[dict] = None
    confidence: Optional[ConfidenceDetail] = None
