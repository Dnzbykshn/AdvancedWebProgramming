# Career Assistant AI Agent

An AI-powered multi-agent system that autonomously communicates with potential employers on your behalf. Built with **FastAPI**, **Google Gemini 2.0 Flash**, **Resend**, and **ntfy.sh**.

> **Advanced Web Programming Homework — Deniz Büyükşahin, 2026**

---

## Architecture

```
Employer Message → FastAPI Backend
                       │
                  [1] ntfy.sh push notification
                       │
                  [2] Unknown Detector (Gemini)
                       │ safe ↓          ↓ flagged → alert + stop
                  [3] Career Agent (Gemini) ← CV + Conversation Memory
                       │
                  [4] Evaluator Agent (Gemini)  score < 7 → revise (max 3×)
                       │ approved
                  [5] Email (Resend) + ntfy push
                       │
                  [7] Store in Conversation Memory
```

---

## Agents & Components

| Component | Description |
|-----------|-------------|
| **Career Agent** | Generates professional email responses grounded in CV data |
| **Evaluator Agent** | LLM-as-a-Judge: scores Tone, Clarity, Completeness, Safety, Relevance |
| **Unknown Detector** | Flags salary, legal, out-of-domain, and sensitive questions |
| **Conversation Memory** | Tracks per-employer message history for multi-turn continuity |
| **Email Tool** | Sends styled HTML emails via Resend API |
| **Notification Tool** | Pushes mobile alerts via ntfy.sh (no account required) |

---

## Setup

### Prerequisites
- Python 3.10+
- API Keys: [Google AI Studio](https://aistudio.google.com/apikey) · [Resend](https://resend.com)
- ntfy app on your phone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/app/ntfy/id1625396347))

### Install
```bash
cd backend
pip install -r requirements.txt
```

### Configure
```bash
copy .env.example .env   # Windows
# Then edit .env and fill in your API keys
```

`.env` keys:
```
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
NTFY_TOPIC=deniz-career-agent
FROM_EMAIL=onboarding@resend.dev
NOTIFY_EMAIL=your_email@example.com
EVALUATOR_THRESHOLD=7
MAX_REVISION_ATTEMPTS=3
```

### Run
```bash
cd backend
python main.py
# or with hot-reload:
python -m uvicorn main:app --reload --port 8000
```

### Open
Navigate to [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/message` | Process an employer message through the full pipeline |
| `GET` | `/api/logs` | View all evaluation logs |
| `DELETE` | `/api/logs` | Clear all logs |
| `GET` | `/api/conversations` | View all conversation histories (grouped by email) |
| `GET` | `/api/conversations/{email}` | View conversation history for a specific employer |
| `DELETE` | `/api/conversations` | Clear all conversation memory |
| `GET` | `/api/health` | Health check |

---

## Frontend Features

- **Message form** — simulate incoming employer messages
- **Pipeline animation** — live step-by-step progress indicator
- **Evaluation score bars** — animated bars for all 5 criteria
- **Confidence gauge** — SVG half-circle meter showing Unknown Detector confidence
- **Conversation thread** — chat-bubble view of the full employer exchange
- **Conversation history panel** — all tracked employers grouped by email
- **Evaluation logs** — history of all processed messages

---

## Project Structure

```
AdvancedWebHW/
├── backend/
│   ├── agents/
│   │   ├── career_agent.py        # Response generation
│   │   └── evaluator_agent.py     # LLM-as-a-Judge scoring
│   ├── data/
│   │   ├── memory.py              # Conversation history store
│   │   └── profile.py             # Candidate CV data
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── prompts/
│   │   ├── career_prompt.py       # Career Agent system prompt
│   │   └── evaluator_prompt.py    # Evaluator system prompt
│   ├── routes/
│   │   └── api.py                 # FastAPI route definitions
│   ├── tools/
│   │   ├── email_tool.py          # Resend email delivery
│   │   ├── notification_tool.py   # ntfy.sh push notifications
│   │   └── unknown_detector.py    # Safety classification
│   ├── config.py                  # Pydantic settings
│   └── main.py                    # FastAPI app entry point
├── docs/
│   ├── architecture.md            # System architecture details
│   ├── test_cases.md              # 3 test cases with results
│   ├── report.md                  # Full project report
│   └── prompts.md                 # Prompt engineering decisions
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Pydantic v2 |
| **AI** | Google Gemini 2.0 Flash |
| **Email** | Resend API (HTTP) |
| **Notifications** | ntfy.sh |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |

---

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Source code | This repository |
| Architecture diagram | `docs/architecture.md` |
| Test cases (3) | `docs/test_cases.md` |
| Project report | `docs/report.md` |
| Prompt design | `docs/prompts.md` |
