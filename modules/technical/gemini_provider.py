import time
import json
import logging
from typing import List, Dict, Any

import config
from modules.technical.ai_provider import BaseAIProvider
from modules.technical.models import QuestionRequest

logger = logging.getLogger("modules.technical.gemini_provider")


class GeminiProvider(BaseAIProvider):

    def __init__(self, api_key: str = None, model_name: str = None):

        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME

        self.max_retries = config.MAX_API_RETRIES
        self.retry_delay = config.RETRY_DELAY_SECONDS

        self.client = None
        self._init_client()

    def _init_client(self):

        if not self.api_key:
            logger.warning("Gemini API key is missing.")
            return

        try:
            from google import genai

            self.client = genai.Client(
                api_key=self.api_key
            )

            logger.info(
                f"Gemini client initialized: {self.model_name}"
            )

        except Exception as e:
            logger.exception(
                f"Gemini client initialization failed: {e}"
            )

    def generate_questions(
        self,
        request: QuestionRequest,
        prompt: str
    ) -> List[Dict[str, Any]]:

        if not self.client:
            raise RuntimeError(
                "Gemini client is not initialized."
            )

        last_exception = None

        for attempt in range(1, self.max_retries + 1):

            try:

                logger.info(
                    f"Gemini request attempt "
                    f"{attempt}/{self.max_retries}"
                )

                from google.genai import types

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                if not response or not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                parsed = json.loads(response.text)

                if isinstance(parsed, dict) and "questions" in parsed:
                    questions = parsed["questions"]

                elif isinstance(parsed, list):
                    questions = parsed

                else:
                    questions = [parsed]

                logger.info(
                    f"Gemini generated {len(questions)} questions."
                )

                return questions

            except Exception as e:

                last_exception = e

                logger.warning(
                    f"Gemini attempt {attempt} failed: {e}"
                )

                if attempt < self.max_retries:

                    delay = self.retry_delay * (2 ** (attempt - 1))

                    logger.info(
                        f"Waiting {delay} seconds before retry..."
                    )

                    time.sleep(delay)

        raise RuntimeError(
            f"Gemini API failed after "
            f"{self.max_retries} attempts. "
            f"Last error: {last_exception}"
        )