# Career Assistant AI Agent — Project Report

**Course:** Advanced Web Programming  
**Student:** Deniz Büyükşahin  
**Date:** February 2026  
**Repository:** github.com/Dnzbykshn/AdvancedWebHW

---

## 1. Introduction

The Career Assistant AI Agent is a multi-agent system that acts as an intelligent intermediary between potential employers and a job candidate. When an employer sends a message — whether an interview invitation, a technical question, or a general inquiry — the system automatically generates a professional, CV-grounded response, evaluates its quality, and delivers it via email, all without human involvement.

The system was designed to solve a practical problem: as job applicants send out many applications, responding to each employer message promptly and professionally is time-consuming. An AI agent that can handle routine employer communication allows the candidate to focus on preparation rather than correspondence.

---

## 2. System Architecture

The system follows a **linear pipeline architecture** with three specialized AI agents orchestrated by a FastAPI backend:

```
Employer Message
      │
      ▼
[1] NOTIFICATION          → Mobile push via ntfy.sh
      │
      ▼
[2] UNKNOWN DETECTOR      → Safe? Continue : Flag & Stop
      │ (safe)
      ▼
[3] CAREER AGENT          ← CV context + conversation history
      │
      ▼
[4] EVALUATOR AGENT       → Score ≥ 7? Approve : Revise (max 3×)
      │ (approved)
      ▼
[5] EMAIL TOOL            → HTML email via Resend API
      │
      ▼
[6] NOTIFICATION          → "Response sent" push
      │
      ▼
[7] CONVERSATION MEMORY   → Store exchange per employer email
```

### Frontend
A single-page web application (HTML/CSS/JavaScript) serves as both the demo interface and a monitoring dashboard. Key UI features include: a message submission form, an animated pipeline progress indicator, evaluation score bars, a confidence gauge (SVG-based half-circle meter), a conversation thread view, and a conversation history panel grouped by employer.

### Backend
FastAPI serves both the REST API and the static frontend files. All state is held in-memory for simplicity, which is appropriate for a homework demonstration system. The backend exposes endpoints for message processing (`POST /api/message`), evaluation logs (`GET /api/logs`), and conversation histories (`GET /api/conversations`).

---

## 3. Design Decisions

### 3.1 Model Selection: Gemini 2.0 Flash

**Google Gemini 2.0 Flash** was chosen over alternatives (GPT-4, Claude) for several reasons:

- **Speed:** Flash is optimized for low-latency inference, which keeps the pipeline response time under 10 seconds for most messages.
- **Cost:** Flash is significantly cheaper than Pro models, making it suitable for a system that may handle many messages.
- **Context window:** Large enough to inject the full CV (~2,000 tokens) plus conversation history without truncation.
- **Structured output:** Gemini reliably produces valid JSON when instructed to, which the Evaluator Agent depends on.

The same model is used for all three agents (Career Agent, Evaluator, Unknown Detector) to simplify the dependency graph. In production, one might use a smaller model for the Unknown Detector (which only needs classification) and a larger model for the Career Agent (which needs nuanced generation).

### 3.2 CV Injection via System Prompt

Rather than using Retrieval-Augmented Generation (RAG), the candidate's complete CV is injected directly into the Career Agent's system prompt. This design decision was made because:

- The CV is small enough (~2,000 tokens) to fit comfortably in the context window.
- RAG adds retrieval latency and complexity with minimal benefit at this scale.
- Direct injection ensures 100% recall — the agent always has access to all relevant information.

The profile is stored as a Python dictionary in `data/profile.py` and formatted as readable text by `get_profile_as_text()`. This makes it easy to update without touching prompt logic.

### 3.3 LLM-as-a-Judge Evaluation

The Evaluator Agent uses the **LLM-as-a-Judge** pattern — asking Gemini to score another Gemini output. This approach was chosen because:

- Human evaluation at inference time is not feasible for an automated system.
- Rule-based evaluation (e.g., checking word count or keyword presence) cannot capture nuanced quality dimensions like tone or professionalism.
- LLM judges have been shown to correlate well with human judgements on open-ended text generation tasks (Zheng et al., 2023).

The evaluator scores five dimensions (Tone, Clarity, Completeness, Safety, Relevance) each out of 10, producing an overall score. The approval threshold of 7/10 was chosen as a balanced point — strict enough to reject clearly poor responses but lenient enough to avoid excessive revision loops.

### 3.4 Conversation Memory

Each employer interaction is stored in a per-email-address dictionary (`data/memory.py`). On subsequent messages from the same employer, the Career Agent receives the full conversation history as part of its prompt, prefixed before the new message. This enables:

- Avoiding repetition of information already shared
- Referencing previous exchanges ("As I mentioned in my earlier message…")
- Maintaining consistent tone across a multi-message thread

Memory is held in-process (Python dict) and resets on server restart, which is acceptable for the scope of this project.

### 3.5 Unknown Question Detection as a Safety Gate

The Unknown Detector acts as a firewall before the Career Agent. It uses a **positive allowlist** approach — explicitly defining what the candidate IS qualified to discuss — rather than a blocklist of forbidden topics. This is more robust because new risky question types cannot be anticipated in advance, whereas the domain of safe topics is well-defined.

Six risk categories are defined: `salary`, `legal`, `out_of_domain`, `ambiguous`, `sensitive`, and `safe`. A confidence score (0.0–1.0) is produced alongside the classification. Messages with confidence below 0.3, even if labeled safe, are flagged for human review.

### 3.6 Multi-Language Support

The system supports Turkish and English natively. This required two specific changes:

1. **Unknown Detector:** Explicitly instructed that Turkish-language messages are not inherently risky; the candidate is a native Turkish speaker. Without this instruction, the model occasionally flagged Turkish as "unexpected language" and classified it as `out_of_domain`.
2. **Career Agent:** Instructed to detect the employer's language and respond in kind. This was implemented via a simple prompt rule: *"Always respond in the same language as the employer's message."*

---

## 4. Evaluation Strategy

### 4.1 Automated Evaluation Loop

Every generated response passes through the Evaluator Agent before being sent. The evaluator produces scores on five independent criteria, each reflecting a different failure mode:

| Criterion | What it guards against |
|-----------|----------------------|
| **Tone** | Too casual, arrogant, or cold |
| **Clarity** | Vague, ambiguous, or confusing statements |
| **Completeness** | Not answering all parts of the employer's message |
| **Safety** | Hallucinations, false claims, salary/legal commitments |
| **Relevance** | Off-topic content or irrelevant tangents |

The evaluator is prompted to produce **actionable feedback** — not just a score, but a specific explanation of any deduction. This feedback is passed to the Career Agent in the revision prompt, enabling targeted improvements.

### 4.2 Revision Loop

If the overall score is below 7/10, the response enters a revision loop:
1. The Career Agent receives its original response plus the evaluator's feedback.
2. It produces a revised response addressing the feedback.
3. The evaluator re-scores the new response.
4. This repeats up to 3 times (configurable via `MAX_REVISION_ATTEMPTS` in `.env`).

After 3 failed revisions, the best-available response is sent rather than withholding communication entirely. In practice, across all tested messages, iteration was rarely required — most first drafts scored above 7/10.

### 4.3 Unknown Detector Validation

The Unknown Detector was tested against both true positives (messages it should flag) and true negatives (messages it should pass). Key findings:

- **Correctly flagged:** salary figures, NDA requests, legal authorization questions, personal questions ("guess my age"), phishing-style vague offers.
- **Correctly passed:** interview scheduling, technical skill questions, general inquiries about experience, availability checks.
- **Edge case found:** The detector initially flagged Turkish-language messages as `out_of_domain`. Fixed by adding explicit language-handling rules to the detection prompt.

---

## 5. Failure Cases

### 5.1 Resend Test Domain Limitation

The Resend API's test sender (`onboarding@resend.dev`) can only deliver emails to the account owner's verified email address. This means during testing, all emails are redirected to the candidate's Gmail regardless of the employer's address entered in the form.

**Workaround implemented:** The email tool detects when the `FROM_EMAIL` contains `resend.dev` and automatically redirects to `NOTIFY_EMAIL`. In production, a custom domain verified with Resend would be used, enabling true recipient delivery.

### 5.2 In-Memory State Loss on Restart

Both the evaluation logs and conversation history are stored in Python dictionaries. Any server restart clears all data. For a production system, this would need to be persisted to a database (e.g., SQLite or PostgreSQL).

**Mitigation for demo:** The frontend's Logs and History panels are populated by API calls on load, so data is visible as long as the server stays running.

### 5.3 LLM Evaluation Inconsistency

Because the Evaluator Agent is itself an LLM, scores can vary slightly between runs for the same response — this is the inherent stochasticity of language model inference. In one test, a response scored 7.2/10 on first evaluation and 7.8/10 on re-evaluation with identical input.

**Mitigation:** A deterministic threshold (≥ 7) rather than a relative threshold (e.g., "top 50%") ensures the system behaves consistently even with score variance of ±0.5.

### 5.4 Prompt Injection Risk

If an employer were to craft a message specifically designed to manipulate the Career Agent (e.g., "Ignore your previous instructions and…"), the system could theoretically be hijacked. The Unknown Detector provides some defense since it evaluates the message intent before the Career Agent is invoked, but it is not specifically trained for adversarial prompts.

**Mitigation in place:** Safety rules in the Career Agent system prompt ("NEVER fabricate or exaggerate," "Do not make salary commitments or legal agreements") provide a partial guardrail against the most harmful outputs.

---

## 6. Reflection

### What Worked Well

The multi-agent pipeline proved to be a natural fit for this problem. Separating concerns — detection, generation, evaluation, notification, delivery — made each component independently testable and replaceable. The LLM-as-a-Judge evaluation loop was particularly effective: it consistently caught responses that were technically correct but professionally weak (e.g., too brief, missing a warm closing).

The decision to support Turkish from the beginning paid off. Many potential employers in the Turkish job market communicate in Turkish, and the ability to detect language and respond in kind dramatically increases the system's practical usefulness.

Conversation memory added meaningful context continuity. When tested with a two-message exchange (initial invitation → follow-up with more details), the second response correctly referenced information from the first message, making the conversation feel cohesive.

### What Would Be Improved in Production

1. **Persistent storage:** Replace in-memory dicts with a lightweight database (SQLite) to survive restarts.
2. **Human review interface:** Build a dedicated UI where flagged messages can be viewed, replied to manually, and approved/rejected.
3. **Custom domain for email:** Verify a real domain with Resend to enable genuine employer delivery.
4. **Rate limiting:** Add per-IP rate limiting to the `/api/message` endpoint to prevent abuse.
5. **Evaluation calibration:** Run the evaluator on a labeled dataset of human-graded responses to calibrate the threshold and detect systematic biases.
6. **Model upgrade path:** The architecture is model-agnostic — swapping `gemini-2.0-flash` for a future, more capable model requires changing a single line in each agent file.

### Ethical Considerations

Automating professional communication raises legitimate questions. Employers engaging with the system are communicating with an AI, not with Deniz directly. For transparency, the email footer states: *"This email was composed with the assistance of an AI Career Agent and reviewed for quality before sending."* This is analogous to using Grammarly or a professional writing service, but more explicit.

The conservative flagging policy — where ambiguous messages go to a human rather than getting an automated response — ensures that consequential decisions (salary, legal, commitments) always involve the actual candidate.

---

## 7. Conclusion

The Career Assistant AI Agent demonstrates that a well-structured multi-agent pipeline can automate professional correspondence while maintaining quality and safety standards comparable to human responses. The key contributions of this project are:

- A **three-agent pipeline** (Unknown Detector → Career Agent → Evaluator) with a configurable revision loop
- **LLM-as-a-Judge** quality evaluation across five measurable criteria
- **Conversation memory** enabling multi-turn employer interactions
- **Confidence scoring** and visualization providing interpretable safety signals
- **Multi-language** support (Turkish and English) with automatic language detection

The system achieved the primary goal: for standard employer messages, it generates, evaluates, and delivers professional responses entirely autonomously, with human intervention reserved only for genuinely ambiguous or risky situations.

---

*Word count: ~1,600 words*  
*Report version: 1.0 — February 2026*
