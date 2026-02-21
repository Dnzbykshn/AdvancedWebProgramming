# Career Assistant AI Agent

An AI-powered multi-agent system that communicates with potential employers on your behalf. Built with **FastAPI**, **Google Gemini API**, **Resend**, and **ntfy.sh**.

## Architecture

```
Employer Message → FastAPI API
                      ↓
               Unknown Detector (Gemini)
                      ↓ (safe)
               Career Agent (Gemini) ← CV/Profile Data
                      ↓
               Evaluator Agent (Gemini)
                      ↓ (score < threshold → revise)
               Approved Response
                ↓            ↓
           Email (Resend)  Notification (ntfy.sh)
```

## Components

| Component | Description |
|-----------|-------------|
| **Career Agent** | Generates professional email responses using your CV data |
| **Evaluator Agent** | LLM-as-a-Judge scoring on tone, clarity, completeness, safety, relevance |
| **Email Tool** | Sends HTML emails via Resend |
| **Notification Tool** | Pushes mobile alerts via ntfy.sh |
| **Unknown Detector** | Flags salary, legal, out-of-domain questions for human review |

## Setup

### 1. Prerequisites
- Python 3.10+
- API Keys: [Google AI Studio](https://aistudio.google.com/apikey), [Resend](https://resend.com)
- ntfy app on your phone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/app/ntfy/id1625396347))

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 4. Subscribe to Notifications
Open the ntfy app on your phone and subscribe to the topic: `deniz-career-agent`

### 5. Run the Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 6. Open the Frontend
Navigate to [http://localhost:8000](http://localhost:8000)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/message` | Process an employer message |
| `GET` | `/api/logs` | View evaluation logs |
| `DELETE` | `/api/logs` | Clear all logs |
| `GET` | `/api/health` | Health check |

## Tech Stack
- **Backend**: Python, FastAPI, Pydantic
- **AI**: Google Gemini 2.0 Flash
- **Email**: Resend API
- **Notifications**: ntfy.sh
- **Frontend**: HTML, CSS, JavaScript (vanilla)

## Author
Deniz Büyükşahin — Advanced Web Programming HW © 2026
