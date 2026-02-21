# System Architecture

## Overview
The Career Assistant AI Agent is a multi-agent system designed to automatically respond to potential employer messages on behalf of a job candidate. The system uses a pipeline architecture with multiple specialized AI agents and tools.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Browser)                              │
│  ┌─────────────┐  ┌─────────────────┐  ┌────────────┐  ┌──────────────┐    │
│  │  Form Input  │  │ Response Display │  │  Eval Bars  │  │  Logs Panel  │    │
│  └──────┬───────┘  └────────▲────────┘  └──────▲─────┘  └──────▲───────┘    │
└─────────┼──────────────────┼────────────────────┼──────────────┼─────────────┘
          │ POST /api/message│                    │              │ GET /api/logs
          ▼                  │                    │              │
┌──────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        API Router (routes/api.py)                       │ │
│  │                                                                         │ │
│  │  Step 1: Notify (ntfy.sh) ──→ 📱 Mobile Push                          │ │
│  │  Step 2: Unknown Detector ──→ Flag? ─→ 📱 Alert + Stop                │ │
│  │  Step 3: Career Agent     ──→ Generate Response                        │ │
│  │  Step 4: Evaluator Agent  ──→ Score < 7? ─→ Revise (loop max 3x)     │ │
│  │  Step 5: Email Tool       ──→ 📧 Send via Resend                      │ │
│  │  Step 6: Notify (ntfy.sh) ──→ 📱 Response Sent                        │ │
│  │  Step 7: Log evaluation   ──→ In-memory store                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  Career Agent     │  │  Evaluator Agent  │  │  Unknown Detector       │   │
│  │  (Gemini 2.0)     │  │  (Gemini 2.0)     │  │  (Gemini 2.0)           │   │
│  │                   │  │                   │  │                          │   │
│  │  System Prompt:   │  │  LLM-as-Judge:    │  │  Classifies messages:    │   │
│  │  - CV context     │  │  - Tone           │  │  - salary               │   │
│  │  - Professional   │  │  - Clarity        │  │  - legal                │   │
│  │    tone rules     │  │  - Completeness   │  │  - out_of_domain        │   │
│  │  - Safety rules   │  │  - Safety         │  │  - ambiguous            │   │
│  │                   │  │  - Relevance      │  │  - sensitive            │   │
│  │  Capabilities:    │  │                   │  │  - safe                 │   │
│  │  - Interview RSVP │  │  Output: JSON     │  │                          │   │
│  │  - Tech Q&A       │  │  {score, feedback}│  │  Output: JSON            │   │
│  │  - Polite decline │  │                   │  │  {is_unknown, reason,    │   │
│  │  - Clarifications │  │                   │  │   confidence, category}  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘   │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  Email Tool       │  │  Notification    │  │  Config                  │   │
│  │  (Resend API)     │  │  Tool (ntfy.sh)  │  │  (Pydantic Settings)     │   │
│  │                   │  │                   │  │                          │   │
│  │  HTML email       │  │  HTTP POST to    │  │  .env file loading       │   │
│  │  formatting       │  │  ntfy.sh/{topic} │  │  API keys, thresholds    │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘

External Services:
  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
  │ Google Gemini  │  │   Resend.com   │  │    ntfy.sh     │
  │ API            │  │   Email API    │  │  Push Service  │
  │                │  │                │  │                │
  │ gemini-2.0-    │  │ HTML email     │  │ Free, no auth  │
  │ flash model    │  │ delivery       │  │ needed         │
  └────────────────┘  └────────────────┘  └────────────────┘
```

## Agent Loop Design

### Primary Flow (Happy Path)
1. Frontend sends `POST /api/message` with employer details
2. Backend notifies mobile device of new message
3. Unknown Detector analyzes message → safe
4. Career Agent generates response with CV context
5. Evaluator Agent scores response on 5 criteria
6. Score ≥ 7 → approved
7. Email sent via Resend, notification pushed via ntfy
8. Response + evaluation returned to frontend

### Revision Loop (Score Below Threshold)
1. Evaluator returns score < 7 with specific feedback
2. Career Agent receives original response + feedback
3. New response generated addressing feedback
4. Evaluator re-evaluates (max 3 revision attempts)
5. Best available response sent after max attempts

### Unknown Question Flow
1. Unknown Detector classifies message as risky
2. Mobile notification sent with urgency flag
3. Event logged for audit trail
4. Frontend shows "Human Intervention Required" alert
5. No automated response is sent

## Tool Invocation Mechanism
All tools are implemented as Python async functions invoked directly by the API router:
- `send_email(to, subject, body)` → Resend API
- `send_notification(title, message, priority)` → ntfy.sh HTTP POST
- `unknown_detector.check(message)` → Gemini classification

## Data Flow
```
EmployerMessage (Pydantic) → API Router → Agent Pipeline → AgentResponse (Pydantic)
                                                         → EvaluationLog (in-memory list)
```
