"""Career Response Agent — generates professional email responses using Gemini API."""

import google.generativeai as genai
from config import settings
from prompts.career_prompt import get_career_system_prompt, get_career_revision_prompt

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class CareerAgent:
    """Primary agent that generates professional email responses on behalf of the candidate."""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=get_career_system_prompt(),
        )

    async def generate_response(
        self, employer_message: str, conversation_context: str = ""
    ) -> str:
        """Generate an initial response to an employer message.

        Args:
            employer_message: The message from the potential employer.
            conversation_context: Optional conversation history context.

        Returns:
            The generated professional email response text.
        """
        prompt_parts = []
        if conversation_context:
            prompt_parts.append(conversation_context)
            prompt_parts.append("\n---\n")
        prompt_parts.append(
            f"Please compose a professional email response to the following employer message:\n\n{employer_message}"
        )

        response = self.model.generate_content("".join(prompt_parts))
        return response.text.strip()

    async def revise_response(
        self, employer_message: str, original_response: str, feedback: str
    ) -> str:
        """Revise a response based on evaluator feedback.

        Args:
            employer_message: Original employer message for context.
            original_response: The response that needs revision.
            feedback: Feedback from the evaluator agent.

        Returns:
            The revised email response text.
        """
        revision_prompt = get_career_revision_prompt(original_response, feedback)
        full_prompt = (
            f"Original employer message:\n{employer_message}\n\n{revision_prompt}"
        )
        response = self.model.generate_content(full_prompt)
        return response.text.strip()
