# ai_client/gemini_client.py
import google.generativeai as genai
from config import settings
from typing import Type  # Add this import for type hinting


class GeminiClient:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

        genai.configure(api_key=settings.GOOGLE_API_KEY)

        # --- THIS IS THE NEW CONFIGURATION ---

        # 1. Define Safety Settings to block harmful content
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # 2. Define Generation Configuration to control output
        self.generation_config = genai.GenerationConfig(
            # We are setting a hard limit on the output. The AI CANNOT exceed this.
            # This prevents the runaway "abomination" response. 4096 is a generous limit.
            max_output_tokens=4096,

            # This is the most important setting for this bug.
            # Temperature controls randomness. 0.9 is creative. 0.2 is very direct and factual.
            # We are telling the AI: "Stop being creative and just give me the answer."
            temperature=0.2
        )

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=safety_settings
            # We will pass the rest of the config during the generate call
        )

    def generate_response(self, prompt: str, schema: Type) -> str:
        """
        Sends a prompt to the Gemini API with strict configuration to ensure
        a focused and well-formed response.
        """
        try:
            # Combine our base config with the specific schema for this request
            request_config = self.generation_config
            request_config.response_mime_type = "application/json"
            request_config.response_schema = schema

            response = self.model.generate_content(
                prompt,
                generation_config=request_config
            )
            return response.text
        except Exception as e:
            print(f"An error occurred while calling the Gemini API: {e}")
            # This will now also catch errors if the model output is blocked by safety settings.
            return ""