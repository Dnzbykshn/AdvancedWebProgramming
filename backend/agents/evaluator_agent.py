"""Response Evaluator Agent — LLM-as-a-Judge that scores and critiques career agent responses."""

import json
import google.generativeai as genai
from config import settings
from prompts.evaluator_prompt import get_evaluator_system_prompt, get_evaluator_user_prompt

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class EvaluationResult:
    """Structured evaluation result from the evaluator agent."""

    def __init__(self, raw: dict):
        self.tone_score: int = raw.get("tone_score", 0)
        self.clarity_score: int = raw.get("clarity_score", 0)
        self.completeness_score: int = raw.get("completeness_score", 0)
        self.safety_score: int = raw.get("safety_score", 0)
        self.relevance_score: int = raw.get("relevance_score", 0)
        self.overall_score: float = raw.get("overall_score", 0.0)
        self.feedback: str = raw.get("feedback", "No feedback provided.")
        self.approved: bool = raw.get("approved", False)

    def to_dict(self) -> dict:
        return {
            "tone_score": self.tone_score,
            "clarity_score": self.clarity_score,
            "completeness_score": self.completeness_score,
            "safety_score": self.safety_score,
            "relevance_score": self.relevance_score,
            "overall_score": self.overall_score,
            "feedback": self.feedback,
            "approved": self.approved,
        }


class EvaluatorAgent:
    """Self-critic agent that evaluates career agent responses before sending."""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=get_evaluator_system_prompt(),
        )

    async def evaluate(
        self, employer_message: str, agent_response: str
    ) -> EvaluationResult:
        """Evaluate a career agent response.

        Args:
            employer_message: The original employer message.
            agent_response: The career agent's generated response.

        Returns:
            EvaluationResult with scores and feedback.
        """
        user_prompt = get_evaluator_user_prompt(
            employer_message, agent_response, settings.EVALUATOR_THRESHOLD
        )

        response = self.model.generate_content(user_prompt)
        raw_text = response.text.strip()

        # Parse JSON from response (handle potential markdown code blocks)
        if raw_text.startswith("```"):
            # Remove markdown code block markers
            raw_text = raw_text.split("\n", 1)[1]  # Remove first line (```json)
            raw_text = raw_text.rsplit("```", 1)[0]  # Remove last ```
            raw_text = raw_text.strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            # Fallback: return a neutral evaluation if JSON parsing fails
            parsed = {
                "tone_score": 5,
                "clarity_score": 5,
                "completeness_score": 5,
                "safety_score": 5,
                "relevance_score": 5,
                "overall_score": 5.0,
                "feedback": f"Failed to parse evaluator response. Raw: {raw_text[:200]}",
                "approved": False,
            }

        return EvaluationResult(parsed)
