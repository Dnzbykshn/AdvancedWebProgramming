"""API route definitions for the Career Assistant Agent."""

from datetime import datetime
from fastapi import APIRouter
from models.schemas import (
    EmployerMessage,
    AgentResponse,
    EvaluationDetail,
    EvaluationLog,
    ConfidenceDetail,
)
from agents.career_agent import CareerAgent
from agents.evaluator_agent import EvaluatorAgent
from tools.unknown_detector import UnknownDetector
from tools.email_tool import send_email
from tools.notification_tool import (
    notify_new_message,
    notify_response_sent,
    notify_unknown_question,
)
from data.memory import memory
from config import settings

router = APIRouter(prefix="/api", tags=["Career Agent"])

# Initialize agents (singleton instances)
career_agent = CareerAgent()
evaluator_agent = EvaluatorAgent()
unknown_detector = UnknownDetector()

# In-memory evaluation logs
evaluation_logs: list[EvaluationLog] = []


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "Career Assistant AI Agent"}


@router.post("/message", response_model=AgentResponse)
async def process_employer_message(message: EmployerMessage):
    """Main endpoint: process an employer message through the full agent pipeline.

    Pipeline:
    1. Notify about new message (ntfy)
    2. Check for unknown/risky questions
    3. Generate career agent response (with conversation context)
    4. Evaluate response (with revision loop)
    5. Send email via Resend
    6. Notify about sent response
    7. Store in conversation memory
    8. Log everything
    """

    # Step 1: Notify about new incoming message
    await notify_new_message(message.sender_name, message.subject)

    # Step 2: Unknown question detection
    detection_result = await unknown_detector.check(message.message)

    # Build confidence detail (always returned, even for safe messages)
    confidence_detail = ConfidenceDetail(
        confidence=detection_result.get("confidence", 0.0),
        category=detection_result.get("category", "unknown"),
        reason=detection_result.get("reason", ""),
        is_unknown=detection_result.get("is_unknown", False),
    )

    # Get conversation history for the response
    conversation_history = memory.get_history(message.sender_email)

    if detection_result.get("is_unknown", False):
        # Flag for human intervention
        await notify_unknown_question(
            message.sender_name, detection_result.get("reason", "Unknown reason")
        )

        # Store in memory (no response sent)
        memory.add_entry(
            sender_email=message.sender_email,
            employer_message=message.message,
            agent_response="",
            status="flagged_unknown",
        )

        # Log the event
        log_entry = EvaluationLog(
            timestamp=datetime.now().isoformat(),
            sender_name=message.sender_name,
            sender_email=message.sender_email,
            subject=message.subject,
            employer_message=message.message,
            status="flagged_unknown",
            unknown_detection=detection_result,
            confidence=confidence_detail,
        )
        evaluation_logs.append(log_entry)

        return AgentResponse(
            status="flagged_unknown",
            response_text="",
            unknown_detection=detection_result,
            confidence=confidence_detail,
            conversation_history=conversation_history,
        )

    # Step 3: Generate initial response with conversation context
    conversation_context = memory.get_context_prompt(message.sender_email)
    response_text = await career_agent.generate_response(
        message.message, conversation_context
    )

    # Step 4: Evaluation loop
    revision_count = 0
    evaluation_result = None

    for attempt in range(settings.MAX_REVISION_ATTEMPTS + 1):
        evaluation_result = await evaluator_agent.evaluate(
            message.message, response_text
        )

        if evaluation_result.approved:
            break

        # If not approved and we have remaining attempts, revise
        if attempt < settings.MAX_REVISION_ATTEMPTS:
            revision_count += 1
            response_text = await career_agent.revise_response(
                message.message, response_text, evaluation_result.feedback
            )

    # Build evaluation detail
    eval_detail = EvaluationDetail(**evaluation_result.to_dict())

    # Step 5: Send email via Resend
    email_result = await send_email(
        to=message.sender_email,
        subject=f"Re: {message.subject}",
        body=response_text,
    )

    # Step 6: Notify about sent response
    notif_result = await notify_response_sent(
        message.sender_name, evaluation_result.overall_score
    )

    # Step 7: Store in conversation memory
    memory.add_entry(
        sender_email=message.sender_email,
        employer_message=message.message,
        agent_response=response_text,
        status="approved",
    )

    # Update conversation history (now includes this exchange)
    conversation_history = memory.get_history(message.sender_email)

    # Step 8: Log the evaluation
    log_entry = EvaluationLog(
        timestamp=datetime.now().isoformat(),
        sender_name=message.sender_name,
        sender_email=message.sender_email,
        subject=message.subject,
        employer_message=message.message,
        response_text=response_text,
        evaluation=eval_detail,
        revision_count=revision_count,
        status="approved",
        confidence=confidence_detail,
    )
    evaluation_logs.append(log_entry)

    return AgentResponse(
        status="approved",
        response_text=response_text,
        evaluation=eval_detail,
        revision_count=revision_count,
        email_result=email_result,
        notification_result=notif_result,
        confidence=confidence_detail,
        conversation_history=conversation_history,
    )


@router.get("/logs")
async def get_evaluation_logs():
    """Return all evaluation logs."""
    return {
        "total": len(evaluation_logs),
        "logs": [log.model_dump() for log in reversed(evaluation_logs)],
    }


@router.delete("/logs")
async def clear_logs():
    """Clear all evaluation logs."""
    evaluation_logs.clear()
    return {"message": "Logs cleared successfully"}


@router.get("/conversations")
async def get_conversations():
    """Return all conversation histories grouped by employer email."""
    conversations = memory.get_all_conversations()
    return {
        "total_employers": len(conversations),
        "conversations": conversations,
    }


@router.get("/conversations/{email}")
async def get_conversation_by_email(email: str):
    """Return the conversation history for a specific employer."""
    history = memory.get_history(email)
    return {
        "email": email,
        "total_messages": len(history),
        "history": history,
    }


@router.delete("/conversations")
async def clear_conversations():
    """Clear all conversation history."""
    memory.clear()
    return {"message": "Conversation history cleared successfully"}
