"""Unknown Question Detection Tool — identifies questions outside the candidate's expertise."""

import json
import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

DETECTION_PROMPT = """You are an Unknown Question Detector for a Career Assistant AI Agent.
Your job is to analyze incoming employer messages and determine if the question/request
is something the AI agent can safely and confidently handle.

## Language Support
The candidate is a NATIVE TURKISH SPEAKER who also speaks English at B2 level.
- Messages in Turkish are COMPLETELY NORMAL and SAFE to handle.
- Messages in English are COMPLETELY NORMAL and SAFE to handle.
- The language of the message alone is NEVER a reason to flag it as unknown.
- Focus ONLY on the CONTENT of the message, not the language it is written in.

## The candidate's domain expertise
- Full-stack web development (Python, Next.js, ASP.NET, FastAPI)
- DevOps & Cloud (AWS, Docker, CI/CD)
- Network administration & cybersecurity (CCNA certified)
- AI/ML integration (Gemini API, RAG architecture)
- Database management (PostgreSQL, MS SQL, Elasticsearch)
- General interview scheduling and availability discussion
- Standard interview questions (e.g., "Why should I hire you?", "Tell me about yourself")

## The agent CANNOT safely handle
1. **Salary negotiation** — beyond mentioning openness to discuss, no specific numbers
2. **Legal questions** — contracts, NDAs, non-competes, visa/immigration details
3. **Deep technical questions outside domain** — e.g., advanced ML theory, FPGA design, biotech
4. **Ambiguous job offers** — vague roles, suspicious requests, MLM-like structures
5. **Personal/sensitive information requests** — SSN, bank details, family info
6. **Medical or psychological questions**
7. **Highly specific company internal knowledge**

## Output Format
Respond with ONLY a valid JSON object:
{
    "is_unknown": <boolean>,
    "confidence": <float 0.0-1.0>,
    "reason": "<explanation of why this is/isn't flagged>",
    "category": "<one of: salary, legal, out_of_domain, ambiguous, sensitive, safe>"
}
"""


class UnknownDetector:
    """Detects when employer messages are outside the agent's safe operating domain."""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=DETECTION_PROMPT,
        )

    async def check(self, employer_message: str) -> dict:
        """Analyze an employer message for unknown/risky content.

        Args:
            employer_message: The incoming message to analyze.

        Returns:
            dict with is_unknown, confidence, reason, and category fields.
        """
        response = self.model.generate_content(
            f"Analyze this employer message:\n\n{employer_message}"
        )
        raw_text = response.text.strip()

        # Parse JSON (handle markdown code blocks)
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("```", 1)[0]
            raw_text = raw_text.strip()

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            # Conservative fallback: flag as unknown if we can't parse
            result = {
                "is_unknown": True,
                "confidence": 0.5,
                "reason": "Failed to analyze message — flagging for human review.",
                "category": "ambiguous",
            }

        # Also flag as unknown if confidence is very low (below 0.3)
        if not result.get("is_unknown") and result.get("confidence", 1.0) < 0.3:
            result["is_unknown"] = True
            result["reason"] = f"Low confidence ({result['confidence']}): " + result.get(
                "reason", "Uncertain analysis"
            )

        return result
