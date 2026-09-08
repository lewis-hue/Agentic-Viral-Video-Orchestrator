import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        if api_key:
            self.client = genai.Client(
                api_key=api_key,
            )
        else:
            self.client = None
            logger.warning("No Google API key configured. Set GOOGLE_CLOUD_API_KEY.")

    def generate_content(self, prompt: str, model: str = "gemini-2.5-flash-preview-09-2025") -> str:
        if not self.client:
            return "API key not configured"
        try:
            result = self.client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            )
            return result.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error: {e}"

# Global instance
gemini_service = GeminiService()