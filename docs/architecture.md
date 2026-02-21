# System Architecture

## Overview
The Career Assistant AI Agent is a multi-agent system that automatically responds to employer messages on behalf of the candidate (Deniz Büyükşahin). It uses a sequential pipeline architecture with three specialized AI agents, conversation memory, and two external notification/delivery tools.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Browser)                                  │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────┐  ┌───────────┐  ┌────────┐  │
│  │  Message  │  │  Confidence   │  │  Eval Score  │  │  Thread   │  │  Logs  │  │
│  │  Form     │  │  Gauge (SVG)  │  │  Bars        │  │  View     │  │  Panel │  │
│  └─────┬─────┘  └───────────────┘  └──────────────┘  └───────────┘  └────────┘  │
└────────┼────────────────────────────────────────────────────────────────────────┘
         │ POST /api/message                                GET /api/logs
         ▼                                                  GET /api/conversations
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             FASTAPI BACKEND                                      │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                       PIPELINE (routes/api.py)                            │    │
│  │                                                                            │    │
│  │  Step 1 ── Notification ─────────────────────────────→ 📱 ntfy.sh         │    │
│  │  Step 2 ── Unknown Detector ──→ flagged? ──→ 📱 Alert + STOP             │    │
│  │                          ↓ safe                                            │    │
│  │  Step 3 ── Career Agent ←── Conversation Memory ←── sender_email key     │    │
│  │                          ↓                                                 │    │
│  │  Step 4 ── Evaluator Agent ──→ score < 7? ──→ Revise → back to step 4    │    │
│  │                          ↓ approved                                        │    │
│  │  Step 5 ── Email Tool ──────────────────────────────→ 📧 Resend API       │    │
│  │  Step 6 ── Notification ─────────────────────────────→ 📱 ntfy.sh         │    │
│  │  Step 7 ── Memory Store ─────────────────────────────→ 💾 In-memory dict  │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │   CAREER AGENT       │  │  EVALUATOR AGENT     │  │  UNKNOWN DETECTOR        │ │
│  │  (Gemini 2.0 Flash)  │  │  (Gemini 2.0 Flash)  │  │  (Gemini 2.0 Flash)      │ │
│  │                       │  │                       │  │                          │ │
│  │  Inputs:              │  │  LLM-as-a-Judge       │  │  Safety classification   │ │
│  │  - Full CV text       │  │  Scores (1–10):       │  │  Categories:             │ │
│  │  - Conversation       │  │  • Tone               │  │  • salary                │ │
│  │    history context    │  │  • Clarity            │  │  • legal                 │ │
│  │  - Employer message   │  │  • Completeness       │  │  • out_of_domain         │ │
│  │                       │  │  • Safety             │  │  • ambiguous             │ │
│  │  Output: email body   │  │  • Relevance          │  │  • sensitive             │ │
│  │  in employer's lang   │  │                       │  │  • safe                  │ │
│  │  (EN or TR)           │  │  Output: JSON         │  │                          │ │
│  │                       │  │  + actionable         │  │  Output: JSON            │ │
│  │                       │  │  feedback             │  │  + confidence score      │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────────────┘ │
│                                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │  CONVERSATION        │  │  EMAIL TOOL          │  │  NOTIFICATION TOOL       │ │
│  │  MEMORY              │  │  (Resend HTTP API)   │  │  (ntfy.sh HTTP POST)     │ │
│  │                       │  │                       │  │                          │ │
│  │  Dict keyed by        │  │  Sends styled HTML    │  │  Priority levels:        │ │
│  │  sender_email         │  │  email to employer    │  │  high = new message      │ │
│  │  (in-memory)          │  │  (or NOTIFY_EMAIL     │  │  default = sent          │ │
│  │                       │  │  for test domain)     │  │  urgent = flagged        │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

External Services:
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  Google Gemini   │   │   Resend.com      │   │    ntfy.sh       │
  │  2.0 Flash       │   │   Email API       │   │   Push Service   │
  │                   │   │                   │   │                  │
  │  All 3 agents    │   │  HTML email       │   │  Free, no user   │
  │  use this model  │   │  delivery         │   │  account needed  │
  └──────────────────┘   └──────────────────┘   └──────────────────┘
```

---

## Agent Loop Design

### Primary Flow (Happy Path)
1. Frontend sends `POST /api/message` with employer name, email, subject, message
2. Backend sends mobile push notification about the new message
3. Unknown Detector analyzes message → classified as `safe`
4. Career Agent fetches conversation history for the sender email
5. Career Agent generates response using CV context + conversation history
6. Evaluator Agent scores response on 5 criteria (all ≥ 7 → approved)
7. Email sent via Resend, confirmation notification pushed via ntfy.sh
8. Exchange stored in Conversation Memory keyed by sender email
9. Full response (including confidence detail + conversation history) returned to frontend

### Revision Loop (Score Below Threshold)
1. Evaluator returns overall_score < 7 with specific actionable feedback
2. Career Agent receives original response + feedback → generates revised response
3. Evaluator re-evaluates revised response
4. Repeat up to `MAX_REVISION_ATTEMPTS` times (default: 3)
5. After max attempts, best-available response is approved and sent

### Unknown Question Flow
1. Unknown Detector classifies message as risky (salary, legal, sensitive, etc.)
2. Confidence score returned (0.0–1.0); messages < 0.3 confidence flagged even if labeled safe
3. High-priority mobile notification sent with urgency flag
4. Exchange stored in memory with status `flagged_unknown` (no response)
5. Frontend shows "Human Intervention Required" alert with reason and category
6. Career Agent and Evaluator are **never invoked**

---

## Tool Invocation Mechanism
All tools are Python async functions invoked directly by the API router:
- `send_email(to, subject, body)` → Resend HTTP API
- `send_notification(title, message, priority, tags)` → ntfy.sh HTTP POST
- `unknown_detector.check(message)` → Gemini classification (returns JSON)
- `memory.get_context_prompt(sender_email)` → formatted conversation history string
- `memory.add_entry(sender_email, message, response, status)` → stores exchange

---

## Data Flow

```
EmployerMessage (Pydantic)
    → API Router
        → UnknownDetector.check()  → ConfidenceDetail
        → memory.get_context_prompt()  → str
        → CareerAgent.generate_response()  → str
        → EvaluatorAgent.evaluate()  → EvaluationDetail
        → send_email() / send_notification()
        → memory.add_entry()
        → EvaluationLog (in-memory list)
    → AgentResponse (Pydantic)
        {status, response_text, evaluation, confidence, conversation_history, ...}
```

---

## Key Design Patterns

| Pattern | Where Used |
|---------|-----------|
| Sequential pipeline | `routes/api.py` — steps 1–7 |
| LLM-as-a-Judge | `evaluator_agent.py` |
| Positive allowlist classification | `unknown_detector.py` DETECTION_PROMPT |
| Context window injection | `career_prompt.py` — CV + history concat |
| Conservative fallback | Unknown Detector — parse failure → flag |
| In-process singleton state | `data/memory.py` — module-level `memory = ConversationMemory()` |
