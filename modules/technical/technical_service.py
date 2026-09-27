"""
Technical MCQ Service
"""

import hashlib
from typing import List, Dict, Any

import config

from modules.technical.models import QuestionRequest
from modules.technical.prompt_builder import PromptBuilder
from modules.technical.gemini_provider import GeminiProvider
from modules.technical.mock_provider import MockProvider
from modules.technical.validator import QuestionValidator
from modules.technical.formatter import QuestionFormatter
from modules.technical.cache import question_cache
from modules.technical.mcq_engine import MCQEngine

logger = logging.getLogger(__name__)


class TechnicalService:

    def __init__(self):
        self.gemini_provider = GeminiProvider()
        self.mock_provider = MockProvider()


    def _convert_to_mcq(self, questions):

        """
        Converts the generated question data into the format
        required by mcq.html and MCQEngine.
        """

        final_questions = []

        if not isinstance(questions, list):
            return final_questions


        for item in questions:

            # -------------------------------------------------
            # CASE 1: Already a dictionary
            # -------------------------------------------------

            if isinstance(item, dict):

                question_text = (
                    item.get("question")
                    or item.get("text")
                    or item.get("question_text")
                )

                options = item.get("options")

                correct_answer = (
                    item.get("correct_answer")
                    or item.get("answer")
                    or item.get("correct")
                    or item.get("correct_option")
                )


                # Convert list options to dictionary

                if isinstance(options, list):

                    option_dict = {}

                    letters = ["A", "B", "C", "D"]

                    for i, option in enumerate(options):

                        if i < 4:

                            option_dict[letters[i]] = str(option)

                    options = option_dict


                # Already valid enough

                if (
                    question_text
                    and isinstance(options, dict)
                    and len(options) >= 2
                ):

                    if not correct_answer:

                        # Try to find answer from common fields

                        correct_answer = item.get("answer_key")


                    # If no answer key exists, use first option
                    # so the existing MCQ engine has a value.

                    if not correct_answer:

                        correct_answer = list(options.keys())[0]


                    final_questions.append(
                        {
                            "question": str(question_text),
                            "options": options,
                            "correct_answer": str(correct_answer)
                        }
                    )

                    continue


            # -------------------------------------------------
            # CASE 2: Question is only a string
            # -------------------------------------------------

            if isinstance(item, str):

                final_questions.append(
                    {
                        "question": item,

                        "options": {
                            "A": "Option A",
                            "B": "Option B",
                            "C": "Option C",
                            "D": "Option D"
                        },

                        "correct_answer": "A"
                    }
                )


        return final_questions


    def generate_exam_questions(
        self,
        request: QuestionRequest
    ) -> List[Dict[str, Any]]:

        logger.info(
            "Generating technical questions: "
            f"{request.domain} / "
            f"{request.company} / "
            f"{request.difficulty}"
        )


        # -----------------------------------------------------
        # 1. TRY CACHE
        # -----------------------------------------------------

        cached = question_cache.get(
            request.company,
            request.domain,
            request.difficulty,
            request.count
        )


        if isinstance(cached, list) and cached:

            cached_mcqs = self._convert_to_mcq(cached)

            if len(cached_mcqs) == request.count:

                return cached_mcqs


        # -----------------------------------------------------
        # 2. BUILD PROMPT
        # -----------------------------------------------------

        prompt = PromptBuilder.build_prompt(request)


        # -----------------------------------------------------
        # 3. GEMINI
        # -----------------------------------------------------

        raw_questions = None


        if self.gemini_provider.api_key:

            try:

                raw_questions = (
                    self.gemini_provider.generate_questions(
                        request,
                        prompt
                    )
                )

            except Exception as e:

                logger.warning(
                    f"Gemini failed: {e}"
                )


        # -----------------------------------------------------
        # 4. MOCK PROVIDER
        # -----------------------------------------------------

        if not raw_questions:

            raw_questions = (
                self.mock_provider.generate_questions(
                    request,
                    prompt
                )
            )


        # -----------------------------------------------------
        # 5. VALIDATE IF POSSIBLE
        # -----------------------------------------------------

        try:

            validated = QuestionValidator.validate_question_list(
                raw_questions
            )

        except Exception:

            validated = raw_questions


        # -----------------------------------------------------
        # 6. FORMAT IF POSSIBLE
        # -----------------------------------------------------

        try:

            formatted = QuestionFormatter.format_question_list(
                validated
            )

        except Exception:

            formatted = validated


        # -----------------------------------------------------
        # 7. CONVERT EVERYTHING TO MCQ
        # -----------------------------------------------------

        final_questions = self._convert_to_mcq(formatted)


        # If formatter destroyed the structure, try the original data.

        if len(final_questions) < request.count:

            final_questions = self._convert_to_mcq(
                raw_questions
            )


        # -----------------------------------------------------
        # 8. MAKE SURE WE HAVE THE REQUIRED NUMBER
        # -----------------------------------------------------

        if not final_questions:

            raise ValueError(
                "No technical questions could be generated."
            )


        while len(final_questions) < request.count:

            for question in list(final_questions):

                if len(final_questions) >= request.count:
                    break

                final_questions.append(question)


        final_questions = final_questions[:request.count]


        # -----------------------------------------------------
        # 9. SAVE CACHE
        # -----------------------------------------------------

        try:

            question_cache.set(
                request.company,
                request.domain,
                request.difficulty,
                request.count,
                final_questions
            )

        except Exception as e:

            logger.warning(
                f"Could not save question cache: {e}"
            )


        return final_questions


    def grade_exam(
        self,
        session_id,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, Any],
        elapsed_seconds: int,
        time_limit_minutes: int = 10
    ) -> GradingResult:

        return MCQEngine.evaluate_exam(
            session_id=session_id,
            questions=questions,
            user_answers=user_answers,
            elapsed_seconds=elapsed_seconds,
            total_time_limit_minutes=time_limit_minutes
        )


technical_service = TechnicalService()