from groq import Groq

from app.config.settings import settings


class GroqService:
    """
    Central service for communicating with Groq.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    def chat(
        self,
        messages,
        model=None,
        temperature=0.2,
    ):
        """
        Send a chat request to Groq.

        Parameters:
            messages: List of chat messages.
            model: Optional Groq model.
            temperature: Response randomness.

        Returns:
            Generated text response.
        """

        if model is None:
            model = settings.GROQ_MODEL

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content


groq_service = GroqService()
