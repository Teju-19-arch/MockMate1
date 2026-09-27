"""
Technical MCQ Service
"""

import logging
from typing import List, Dict, Any

from modules.technical.models import (
    QuestionRequest,
    GradingResult
)

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


    # ========================================================================
    # CONVERT GENERATED QUESTIONS INTO MCQ FORMAT
    # ========================================================================

    def _convert_to_mcq(self, questions):

        """
        Converts generated question data into the format
        required by mcq.html and MCQEngine.

        Final question format:

        {
            "question": "...",
            "options": {
                "A": "...",
                "B": "...",
                "C": "...",
                "D": "..."
            },
            "correct_option": "A",
            "explanation": "..."
        }
        """

        final_questions = []

        if not isinstance(questions, list):
            return final_questions


        for item in questions:

            # =================================================================
            # CASE 1: QUESTION IS A DICTIONARY
            # =================================================================

            if isinstance(item, dict):

                question_text = (
                    item.get("question")
                    or item.get("text")
                    or item.get("question_text")
                )

                options = item.get("options")

                correct_answer = (
                    item.get("correct_option")
                    or item.get("correct_answer")
                    or item.get("answer")
                    or item.get("correct")
                    or item.get("answer_key")
                )

                explanation = item.get(
                    "explanation",
                    ""
                )


                # -------------------------------------------------------------
                # Convert list options to dictionary
                # -------------------------------------------------------------

                if isinstance(options, list):

                    option_dict = {}

                    letters = [
                        "A",
                        "B",
                        "C",
                        "D"
                    ]

                    for i, option in enumerate(options):

                        if i < 4:

                            option_dict[
                                letters[i]
                            ] = str(option)

                    options = option_dict


                # -------------------------------------------------------------
                # Make sure options are a dictionary
                # -------------------------------------------------------------

                if isinstance(options, dict):

                    normalized_options = {}

                    for key, value in options.items():

                        normalized_key = str(
                            key
                        ).strip().upper()

                        normalized_options[
                            normalized_key
                        ] = str(value)

                    options = normalized_options


                # -------------------------------------------------------------
                # Validate basic structure
                # -------------------------------------------------------------

                if (
                    question_text
                    and isinstance(options, dict)
                    and len(options) >= 2
                ):

                    # ---------------------------------------------------------
                    # If answer is missing, use first option.
                    # Normally Gemini should always provide the answer.
                    # ---------------------------------------------------------

                    if not correct_answer:

                        correct_answer = list(
                            options.keys()
                        )[0]


                    correct_answer = str(
                        correct_answer
                    ).strip().upper()


                    # ---------------------------------------------------------
                    # If Gemini returned something like:
                    #
                    # "A"
                    #
                    # keep it.
                    #
                    # If it returned a full option text, try to find
                    # the matching option.
                    # ---------------------------------------------------------

                    if correct_answer not in options:

                        matched_key = None

                        for key, value in options.items():

                            if (
                                str(value).strip().lower()
                                == correct_answer.lower()
                            ):

                                matched_key = key
                                break


                        if matched_key:

                            correct_answer = matched_key

                        else:

                            correct_answer = list(
                                options.keys()
                            )[0]


                    final_questions.append(
                        {
                            "question": str(
                                question_text
                            ),

                            "options": options,

                            "correct_option": correct_answer,

                            "explanation": str(
                                explanation
                            )
                        }
                    )

                    continue


            # =================================================================
            # CASE 2: QUESTION IS ONLY A STRING
            # =================================================================

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

                        "correct_option": "A",

                        "explanation": ""
                    }
                )


        return final_questions


    # ========================================================================
    # GENERATE EXAM QUESTIONS
    # ========================================================================

    def generate_exam_questions(
        self,
        request: QuestionRequest,
        resume_text: str = ""
    ) -> List[Dict[str, Any]]:

        """
        Generates technical MCQ questions.

        Resume is optional.

        If resume_text is provided:
            Questions are personalized using the resume.

        If resume_text is empty:
            Questions are generated using the selected
            domain/company and difficulty.
        """

        resume_text = resume_text or ""

        has_resume = bool(
            resume_text.strip()
        )


        logger.info(
            "Generating technical questions: "
            f"Mode={request.mode}, "
            f"Domain={request.domain}, "
            f"Company={request.company}, "
            f"Difficulty={request.difficulty}, "
            f"Count={request.count}, "
            f"Resume={'YES' if has_resume else 'NO'}"
        )


        # ====================================================================
        # 1. CACHE
        # ====================================================================

        """
        Resume-based questions are NOT read from cache.

        This is important because the normal cache does not contain
        resume information. Using it for a resume assessment could
        return questions generated for another candidate.
        """

        if not has_resume:

            try:

                cached = question_cache.get(
                    request.company,
                    request.domain,
                    request.difficulty,
                    request.count
                )

                if (
                    isinstance(cached, list)
                    and cached
                ):

                    cached_mcqs = (
                        self._convert_to_mcq(
                            cached
                        )
                    )

                    if len(cached_mcqs) == request.count:

                        logger.info(
                            "Using cached technical questions."
                        )

                        return cached_mcqs

            except Exception as e:

                logger.warning(
                    f"Could not read question cache: {e}"
                )

        else:

            logger.info(
                "Resume detected. "
                "Skipping question cache."
            )


        # ====================================================================
        # 2. BUILD PROMPT
        # ====================================================================

        try:

            prompt = PromptBuilder.build_prompt(
                request,
                resume_text=resume_text
            )

        except TypeError:

            """
            Compatibility fallback in case an older PromptBuilder
            implementation is present.
            """

            logger.warning(
                "PromptBuilder does not accept resume_text. "
                "Using legacy prompt builder."
            )

            prompt = PromptBuilder.build_prompt(
                request
            )


        # ====================================================================
        # 3. GEMINI
        # ====================================================================

        raw_questions = None


        if self.gemini_provider.api_key:

            try:

                logger.info(
                    "Generating questions using Gemini..."
                )

                raw_questions = (
                    self.gemini_provider.generate_questions(
                        request,
                        prompt
                    )
                )

                logger.info(
                    "Gemini returned "
                    f"{len(raw_questions) if raw_questions else 0} "
                    "questions."
                )

            except Exception as e:

                logger.warning(
                    f"Gemini failed: {e}"
                )


        # ====================================================================
        # 4. MOCK PROVIDER FALLBACK
        # ====================================================================

        if not raw_questions:

            logger.warning(
                "Gemini did not return questions. "
                "Using MockProvider fallback."
            )

            raw_questions = (
                self.mock_provider.generate_questions(
                    request,
                    prompt
                )
            )


        # ====================================================================
        # 5. VALIDATE QUESTIONS
        # ====================================================================

        try:

            validated = (
                QuestionValidator.validate_question_list(
                    raw_questions
                )
            )

        except Exception as e:

            logger.warning(
                f"Question validation failed: {e}"
            )

            validated = raw_questions


        # ====================================================================
        # 6. FORMAT QUESTIONS
        # ====================================================================

        try:

            formatted = (
                QuestionFormatter.format_question_list(
                    validated
                )
            )

        except Exception as e:

            logger.warning(
                f"Question formatting failed: {e}"
            )

            formatted = validated


        # ====================================================================
        # 7. CONVERT TO FINAL MCQ FORMAT
        # ====================================================================

        final_questions = (
            self._convert_to_mcq(
                formatted
            )
        )


        # ====================================================================
        # 8. FALLBACK TO RAW QUESTIONS
        # ====================================================================

        if len(final_questions) < request.count:

            logger.warning(
                "Formatted questions were insufficient. "
                "Trying raw questions."
            )

            final_questions = (
                self._convert_to_mcq(
                    raw_questions
                )
            )


        # ====================================================================
        # 9. CHECK QUESTIONS
        # ====================================================================

        if not final_questions:

            raise ValueError(
                "No technical questions could be generated."
            )


        # ====================================================================
        # 10. ENSURE REQUIRED QUESTION COUNT
        # ====================================================================

        while len(final_questions) < request.count:

            current_questions = list(
                final_questions
            )

            for question in current_questions:

                if len(final_questions) >= request.count:
                    break

                final_questions.append(
                    question.copy()
                )


        final_questions = (
            final_questions[:request.count]
        )


        # ====================================================================
        # 11. CACHE NON-RESUME QUESTIONS ONLY
        # ====================================================================

        if not has_resume:

            try:

                question_cache.set(
                    request.company,
                    request.domain,
                    request.difficulty,
                    request.count,
                    final_questions
                )

                logger.info(
                    "Technical questions saved to cache."
                )

            except Exception as e:

                logger.warning(
                    f"Could not save question cache: {e}"
                )

        else:

            logger.info(
                "Resume-based questions were not cached."
            )


        # ====================================================================
        # 12. FINAL LOGGING
        # ====================================================================

        logger.info(
            "Technical question generation complete. "
            f"Questions={len(final_questions)}, "
            f"Resume personalization="
            f"{'ENABLED' if has_resume else 'DISABLED'}"
        )


        return final_questions


    # ========================================================================
    # GRADE EXAM
    # ========================================================================

    def grade_exam(
        self,
        session_id,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, Any],
        elapsed_seconds: int,
        time_limit_minutes: int = 10
    ) -> GradingResult:

        """
        Evaluate the submitted technical MCQ assessment.
        """

        logger.info(
            "Evaluating technical assessment..."
        )

        result = MCQEngine.evaluate_exam(

            session_id=session_id,

            questions=questions,

            user_answers=user_answers,

            elapsed_seconds=elapsed_seconds,

            total_time_limit_minutes=time_limit_minutes
        )


        logger.info(
            "Assessment evaluated. "
            f"Score={result.score}/"
            f"{result.total_marks}, "
            f"Correct={result.correct_count}/"
            f"{result.total_questions}, "
            f"Accuracy={result.accuracy_percentage}%"
        )


        return result


# ============================================================================
# TECHNICAL SERVICE INSTANCE
# ============================================================================

technical_service = TechnicalService()