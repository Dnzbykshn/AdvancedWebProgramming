# Prompt Design Documentation

## Overview
This document describes the prompt engineering decisions for each AI agent in the Career Assistant system. All agents use **Google Gemini 2.0 Flash** for fast, cost-effective inference.

---

## 1. Career Agent Prompt

### Purpose
Generate professional email responses on behalf of the candidate (Deniz Büyükşahin).

### Design Decisions

**Identity Injection**: The system prompt explicitly embeds the full CV/profile as structured text. This ensures the model has complete context about skills, experience, and qualifications without needing retrieval augmentation.

**Tone Control**: Specific guidelines enforce "professional, warm, and confident — never arrogant or overly casual." This prevents both overly formal corporate-speak and informal chat-like responses.

**Safety Guardrails**:
- "ONLY reference skills, experiences, and qualifications listed above"
- "NEVER fabricate or exaggerate"
- "Do not make salary commitments, legal agreements, or promises"

**Capability Coverage**: The prompt explicitly lists the four required capabilities:
1. Accepting interview invitations
2. Responding to technical questions
3. Politely declining offers
4. Asking clarifying questions

**Output Format**: "Respond ONLY with the email body text" — prevents the model from wrapping responses in JSON or metadata.

### Revision Prompt
When a response needs revision, the revision prompt includes:
- The original response text
- The evaluator's specific feedback
- Instructions to address ALL feedback points

This creates a feedback loop where the agent can iteratively improve.

---

## 2. Evaluator Agent Prompt

### Purpose
Score career agent responses as an LLM-as-a-Judge before sending.

### Design Decisions

**Structured JSON Output**: The evaluator is forced to output a strict JSON format with 5 individual scores plus an overall score. This enables:
- Programmatic parsing
- Visual score bars in the frontend
- Threshold-based approval logic

**5 Evaluation Criteria**:
| Criterion | Why |
|-----------|-----|
| **Tone** | Ensures professional email etiquette |
| **Clarity** | Guards against vague or confusing responses |
| **Completeness** | Verifies all employer questions are answered |
| **Safety** | Catches hallucinations, false claims, risky commitments |
| **Relevance** | Ensures the response addresses the actual message |

**Threshold-Based Approval**: `overall_score >= 7` triggers approval. This was chosen as a balanced threshold — strict enough to catch poor responses but not so strict that every response requires revision.

**Actionable Feedback**: The feedback field must provide "specific, actionable feedback explaining any deductions." This ensures the career agent has clear revision instructions.

---

## 3. Unknown Question Detector Prompt

### Purpose
Classify incoming employer messages to determine if the AI agent can safely respond.

### Design Decisions

**Domain Expertise Mapping**: The prompt explicitly lists what the candidate IS qualified to discuss, creating a positive allowlist rather than just a blocklist.

**Risk Categories**: Six categories with examples:
1. `salary` — specific number negotiations
2. `legal` — contracts, NDAs, visa questions
3. `out_of_domain` — topics beyond listed skills
4. `ambiguous` — vague or suspicious offers
5. `sensitive` — personal data requests
6. `safe` — normal career communication

**Confidence Scoring**: The detector outputs a confidence float (0.0–1.0). Messages with confidence < 0.3 are automatically flagged, even if classified as safe. This adds a safety net for edge cases.

**Conservative Fallback**: If JSON parsing fails, the message is flagged as unknown (false positive > false negative). This is intentional — it's better to ask a human than to send a risky automated response.

---

## Prompt Evolution Strategy
All prompts are stored in the `prompts/` directory as Python functions, making them easy to:
- Version control
- A/B test different prompt variants
- Add few-shot examples in the future
- Swap between models (Flash vs Pro)
