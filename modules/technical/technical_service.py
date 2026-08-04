"""
modules/technical/technical_service.py
---------------------------------------
Workflow Coordinator Service for Technical Interview Module.
Orchestrates caching, prompt building, AI provider execution (Gemini/Mock),
JSON schema validation, text formatting, and exam grading.
"""

import logging
from typing import List, Dict, Any

from modules.technical.models import QuestionRequest, GradingResult
from modules.technical.prompt_builder import PromptBuilder
from modules.technical.gemini_provider import GeminiProvider
from modules.technical.mock_provider import MockProvider
from modules.technical.validator import QuestionValidator
from modules.technical.formatter import QuestionFormatter
from modules.technical.cache import question_cache
from modules.technical.mcq_engine import MCQEngine

logger = logging.getLogger("modules.technical.technical_service")


class TechnicalService:
    """
    Central service class orchestrating technical interview workflows.
    """

    def __init__(self):
        self.gemini_provider = GeminiProvider()
        self.mock_provider = MockProvider()

    def generate_exam_questions(self, request: QuestionRequest) -> List[Dict[str, Any]]:
        """
        Coordinates fetching, validating, formatting, and caching technical MCQs.

        Flow:
        1. Check QuestionCache for cached response.
        2. Build LLM prompt via PromptBuilder.
        3. Attempt generation via GeminiProvider; fallback to MockProvider on error.
        4. Validate JSON structure via QuestionValidator.
        5. Format and sanitize via QuestionFormatter.
        6. Store result in QuestionCache.
        7. Return sanitized question list.
        """
        logger.info(f"Generating technical exam questions: Mode={request.mode}, Domain={request.domain}, Company={request.company}, Difficulty={request.difficulty}")

        # 1. Check Cache
        cached = question_cache.get(request.company, request.domain, request.difficulty, request.count)
        if cached and len(cached) == request.count:
            logger.info("Serving questions from QuestionCache.")
            return cached

        # 2. Build Prompt
        prompt = PromptBuilder.build_prompt(request)

        # 3. Attempt Gemini API Generation with Fallback to Mock Provider
        raw_questions = None
        if self.gemini_provider.api_key:
            try:
                raw_questions = self.gemini_provider.generate_questions(request, prompt)
            except Exception as e:
                logger.warning(f"GeminiProvider failed: {e}. Falling back to MockProvider.")

        if not raw_questions:
            raw_questions = self.mock_provider.generate_questions(request, prompt)

        # Ensure raw_questions has exactly request.count items
        if raw_questions and len(raw_questions) < request.count:
            logger.warning(f"Provider returned {len(raw_questions)} questions, expected {request.count}. Padding questions.")
            padded = []
            while len(padded) < request.count:
                for q in raw_questions:
                    if len(padded) >= request.count:
                        break
                    padded.append(q)
            raw_questions = padded
        elif raw_questions and len(raw_questions) > request.count:
            raw_questions = raw_questions[:request.count]

        # 4. Validate JSON Schema
        validated = QuestionValidator.validate_question_list(raw_questions)

        # 5. Format & Sanitize
        formatted = QuestionFormatter.format_question_list(validated)

        # 6. Store in Cache
        question_cache.set(request.company, request.domain, request.difficulty, request.count, formatted)

        return formatted

    def grade_exam(
        self,
        session_id: int,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, str],
        elapsed_seconds: int,
        time_limit_minutes: int = 10
    ) -> GradingResult:
        """
        Delegates grading and metrics evaluation to MCQEngine.
        """
        return MCQEngine.evaluate_exam(
            session_id=session_id,
            questions=questions,
            user_answers=user_answers,
            elapsed_seconds=elapsed_seconds,
            total_time_limit_minutes=time_limit_minutes
        )


# Global service instance
technical_service = TechnicalService()
