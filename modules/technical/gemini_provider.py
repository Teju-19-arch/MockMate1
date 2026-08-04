"""
modules/technical/gemini_provider.py
------------------------------------
Google Gemini API Provider implementation for MCQ Question Generation.
Includes exponential retry logic, timeout handling, and JSON response extraction.
"""

import time
import json
import logging
from typing import List, Dict, Any

import config
from modules.technical.ai_provider import BaseAIProvider
from modules.technical.models import QuestionRequest

logger = logging.getLogger("modules.technical.gemini_provider")


class GeminiProvider(BaseAIProvider):
    """
    Concrete AI Provider integrating Google Gemini API for MCQ generation.
    """

    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME
        self.max_retries = config.MAX_API_RETRIES
        self.retry_delay = config.RETRY_DELAY_SECONDS
        self._init_client()

    def _init_client(self):
        """Initializes Google Generative AI client if API key is present."""
        self.genai_client = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai_client = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini API Provider initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to configure google.generativeai client: {e}")

    def generate_questions(self, request: QuestionRequest, prompt: str) -> List[Dict[str, Any]]:
        """
        Generates technical MCQ questions using Google Gemini API with retries.
        """
        if not self.genai_client:
            raise RuntimeError("Gemini API key is missing or client is not configured.")

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Invoking Gemini API (Attempt {attempt}/{self.max_retries})...")
                
                # Request JSON output from Gemini
                generation_config = {
                    "temperature": 0.7,
                    "response_mime_type": "application/json",
                }
                
                response = self.genai_client.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                if response and response.text:
                    raw_json = response.text.strip()
                    parsed = json.loads(raw_json)
                    
                    # Ensure top-level list
                    if isinstance(parsed, dict) and "questions" in parsed:
                        questions_list = parsed["questions"]
                    elif isinstance(parsed, list):
                        questions_list = parsed
                    else:
                        questions_list = [parsed]
                        
                    logger.info(f"Gemini API returned {len(questions_list)} raw questions successfully.")
                    return questions_list
                else:
                    raise ValueError("Received empty text response from Gemini API.")

            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini API attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    sleep_time = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        raise RuntimeError(f"Gemini API failed after {self.max_retries} attempts. Last error: {last_exception}")
