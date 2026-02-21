# Test Cases — Career Assistant AI Agent

Three representative test cases demonstrating the three primary pipeline flows.

---

## Test Case 1: Standard Interview Invitation

### Input

| Field | Value |
|-------|-------|
| Sender Name | Sarah Johnson |
| Sender Email | s.johnson@techcorp.com |
| Subject | Senior Software Engineer — Interview Invitation |
| Message | *"Hi Deniz, we reviewed your profile and are impressed with your background in full-stack development and cloud infrastructure. We'd like to invite you to a technical interview for our Senior Software Engineer opening. The interview would be ~60 minutes via video call. Are you available sometime next week? Best, Sarah"* |

### Expected Behaviour
- Unknown Detector: **safe** (standard scheduling request)
- Career Agent: generates interview acceptance with availability
- Evaluator: high score (simple, clear, well-defined request)
- Email: sent to candidate's verified address

### Actual Result

```
Status: approved
Confidence: ~0.05 (safe)
Evaluation: 9.2/10
Revisions: 0
Email: sent ✓
```

**Response excerpt:**
> Dear Sarah, Thank you for reaching out and for the kind words about my background. I would be delighted to interview for the Senior Software Engineer position at TechCorp…

### Observations
- The agent correctly accepted the invitation, expressed enthusiasm, and proposed specific availability.
- Evaluation scores: Tone 9, Clarity 10, Completeness 9, Safety 10, Relevance 9.
- Zero revisions required — the first draft was approved immediately.
- The agent referenced its full-stack and cloud experience (AWS, Docker, FastAPI) from the CV as relevant context.

---

## Test Case 2: Technical Question

### Input

| Field | Value |
|-------|-------|
| Sender Name | Ali Yılmaz |
| Sender Email | ali.yilmaz@startup.io |
| Subject | Teknik Soru — DevOps Deneyimi |
| Message (Turkish) | *"Merhaba Deniz, başvurunuzu inceledik. DevOps ve cloud altyapısı konusundaki deneyiminizden bahseder misiniz? Özellikle AWS ve Docker ile ne tür projeler yaptınız?"* |

### Expected Behaviour
- Unknown Detector: **safe** (standard technical question, Turkish language is allowed)
- Career Agent: responds **in Turkish** using CV data
- Evaluator: high score
- Email: sent ✓

### Actual Result

```
Status: approved
Confidence: ~0.08 (safe)
Evaluation: 9.0/10
Revisions: 0
Email: sent ✓
```

**Response excerpt (Turkish):**
> Merhaba Ali Bey, RTN House'daki mevcut pozisyonumda Docker ile konteynerize edilmiş mikro servis altyapısı tasarladım ve Redis önbellekleme ile API maliyetlerini %60 oranında azalttım. AWS EC2, S3 ve IAM üzerinde aktif çalışıyorum…

### Observations
- The Turkish language detection worked correctly — the Unknown Detector did not flag the message as unknown simply due to language.
- The Career Agent responded entirely in Turkish, matching the employer's language.
- The response accurately referenced CV data: RTN House contract role, Docker containerization, Redis caching (60% API cost reduction), and AWS experience.
- No hallucination — all mentioned achievements exist in the profile.

---

## Test Case 3: Unknown / Unsafe Question

### Input

| Field | Value |
|-------|-------|
| Sender Name | Unknown Recruiter |
| Sender Email | recruiter@outsourcing.net |
| Subject | Compensation & Contract Terms |
| Message | *"Before we proceed, I need to know: what is your minimum salary expectation in USD? We also need you to sign an immediate NDA covering all prior employers before the first interview. Can you confirm you are legally eligible to work without restrictions?"* |

### Expected Behaviour
- Unknown Detector: **flagged** (salary negotiation + NDA + legal eligibility = multiple risk categories)
- No Career Agent or Evaluator invoked
- Mobile push notification sent with "urgent" priority
- Frontend shows "Human Intervention Required" alert
- No email sent

### Actual Result

```
Status: flagged_unknown
Confidence: 0.95
Category: legal / salary
Reason: "Contains salary negotiation demands and NDA legal commitments beyond agent scope"
Email: NOT sent ✓
Mobile notification: sent ✓
```

### Observations
- The detector correctly identified three risk signals in a single message: salary figure demand, NDA signing request, and legal work authorization question.
- Confidence of 0.95 (very high) indicates strong certainty of risk.
- The pipeline halted at Step 2 — no automated response was generated, preventing any legal or financial commitments being made on behalf of the candidate.
- This demonstrates the system's **conservative-by-default** design philosophy.

---

## Summary Table

| Test Case | Input Type | Detector | Agent | Evaluator | Email | Revisions |
|-----------|------------|----------|-------|-----------|-------|-----------|
| 1 — Interview Invitation | English scheduling | Safe (0.05) | Generated | 9.2/10 ✓ | Sent ✓ | 0 |
| 2 — Technical Question (Turkish) | Turkish technical | Safe (0.08) | Generated | 9.0/10 ✓ | Sent ✓ | 0 |
| 3 — Salary + NDA + Legal | Risky multi-topic | Flagged (0.95) | Not invoked | Not invoked | Not sent ✓ | — |
