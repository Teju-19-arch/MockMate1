"""
modules/technical/technical_service.py
---------------------------------------

Technical MCQ service for MockMate.

Responsibilities:
- Generate MCQs using Gemini
- Personalize questions using resume text
- Validate Gemini output
- Normalize question structure
- Cache questions when enabled
- Grade submitted answers
"""

import hashlib
from typing import List, Dict, Any

import config

from modules.technical.models import QuestionRequest
from modules.technical.prompt_builder import PromptBuilder
from modules.technical.gemini_provider import GeminiProvider
from modules.technical.cache import QuestionCache


class TechnicalService:

    def __init__(self):
        """
        Initialize the technical assessment service.
        """

        self.provider = GeminiProvider()

        self.cache = QuestionCache()


    # ------------------------------------------------------------------
    # Cache Key
    # ------------------------------------------------------------------

    def _build_cache_key(
        self,
        request: QuestionRequest,
        resume_text: str = None
    ) -> str:
        """
        Create a unique cache key.

        Resume content is included so that different candidates
        do not receive the same cached personalized questions.
        """

        resume_hash = ""

        if resume_text:
            resume_hash = hashlib.sha256(
                resume_text.encode("utf-8")
            ).hexdigest()

        return "|".join(
            [
                str(request.mode or ""),
                str(request.domain or ""),
                str(request.company or ""),
                str(request.difficulty or ""),
                str(request.count),
                resume_hash
            ]
        )


    # ------------------------------------------------------------------
    # Normalize Question
    # ------------------------------------------------------------------

    def _normalize_question(
        self,
        question: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Normalize one Gemini-generated question.

        Expected Gemini structure:

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

        if not isinstance(question, dict):
            return None


        question_text = str(
            question.get(
                "question",
                ""
            )
        ).strip()


        if not question_text:
            return None


        # --------------------------------------------------------------
        # Get options
        # --------------------------------------------------------------

        options = question.get(
            "options",
            {}
        )


        if not isinstance(options, dict):
            return None


        normalized_options = {}

        for letter in ["A", "B", "C", "D"]:

            value = options.get(
                letter
            )

            if value is None:

                # Sometimes Gemini may return lowercase keys.
                value = options.get(
                    letter.lower()
                )

            if value is None:

                return None

            value = str(
                value
            ).strip()

            if not value:

                return None

            normalized_options[letter] = value


        # --------------------------------------------------------------
        # Correct answer
        # --------------------------------------------------------------

        correct_option = (
            question.get(
                "correct_option"
            )
            or question.get(
                "correct_answer"
            )
            or question.get(
                "answer"
            )
        )


        if correct_option is None:
            return None


        correct_option = str(
            correct_option
        ).strip().upper()


        # Handle answers such as:
        # "A)"
        # "A."
        # "Option A"

        if correct_option.startswith("OPTION "):

            correct_option = correct_option.replace(
                "OPTION ",
                ""
            ).strip()


        if correct_option.startswith("A"):

            if correct_option in [
                "A",
                "A)",
                "A."
            ]:
                correct_option = "A"

        elif correct_option.startswith("B"):

            if correct_option in [
                "B",
                "B)",
                "B."
            ]:
                correct_option = "B"

        elif correct_option.startswith("C"):

            if correct_option in [
                "C",
                "C)",
                "C."
            ]:
                correct_option = "C"

        elif correct_option.startswith("D"):

            if correct_option in [
                "D",
                "D)",
                "D."
            ]:
                correct_option = "D"


        if correct_option not in [
            "A",
            "B",
            "C",
            "D"
        ]:

            return None


        # --------------------------------------------------------------
        # Explanation
        # --------------------------------------------------------------

        explanation = str(
            question.get(
                "explanation",
                ""
            )
        ).strip()


        # --------------------------------------------------------------
        # Return normalized question
        # --------------------------------------------------------------

        return {
            "question": question_text,

            "options": normalized_options,

            "correct_option": correct_option,

            "explanation": explanation
        }


    # ------------------------------------------------------------------
    # Validate Questions
    # ------------------------------------------------------------------

    def _validate_questions(
        self,
        questions: Any,
        expected_count: int
    ) -> List[Dict[str, Any]]:
        """
        Validate and normalize Gemini output.

        Invalid questions are removed.
        """

        if not isinstance(
            questions,
            list
        ):

            raise RuntimeError(
                "Gemini returned an invalid question format."
            )


        valid_questions = []


        for question in questions:

            normalized = self._normalize_question(
                question
            )

            if normalized:

                valid_questions.append(
                    normalized
                )


        if not valid_questions:

            raise RuntimeError(
                "Gemini returned no valid MCQ questions."
            )


        # --------------------------------------------------------------
        # Remove duplicate questions
        # --------------------------------------------------------------

        unique_questions = []

        seen = set()


        for question in valid_questions:

            key = question[
                "question"
            ].strip().lower()


            if key in seen:

                continue


            seen.add(
                key
            )

            unique_questions.append(
                question
            )


        valid_questions = unique_questions


        # --------------------------------------------------------------
        # Limit to requested count
        # --------------------------------------------------------------

        if len(valid_questions) > expected_count:

            valid_questions = valid_questions[
                :expected_count
            ]


        return valid_questions


    # ------------------------------------------------------------------
    # Generate Exam Questions
    # ------------------------------------------------------------------

    def generate_exam_questions(
        self,
        request: QuestionRequest,
        resume_text: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized technical MCQs.

        Questions are based on:
        - Selected domain
        - Selected company
        - Difficulty
        - Number of questions
        - Uploaded resume
        """

        if request is None:

            raise ValueError(
                "Question request is required."
            )


        # --------------------------------------------------------------
        # Validate count
        # --------------------------------------------------------------

        count = int(
            request.count
        )


        if count < 1:

            raise ValueError(
                "Question count must be at least 1."
            )


        if count > 20:

            raise ValueError(
                "Question count cannot exceed 20."
            )


        # --------------------------------------------------------------
        # Cache key
        # --------------------------------------------------------------

        cache_key = self._build_cache_key(
            request,
            resume_text
        )


        # --------------------------------------------------------------
        # Cache
        # --------------------------------------------------------------

        if config.ENABLE_QUESTION_CACHE:

            try:

                cached = self.cache.get(
                    cache_key
                )

                if cached:

                    print(
                        "[TECHNICAL SERVICE] "
                        "Using cached questions."
                    )

                    return cached

            except Exception as e:

                print(
                    "[TECHNICAL SERVICE] "
                    f"Cache read failed: {e}"
                )


        # --------------------------------------------------------------
        # Build prompt
        # --------------------------------------------------------------

        print(
            "[TECHNICAL SERVICE] "
            "Building personalized Gemini prompt..."
        )


        prompt = PromptBuilder.build_prompt(
            request,
            resume_text=resume_text
        )


        # --------------------------------------------------------------
        # Generate questions
        # --------------------------------------------------------------

        print(
            "[TECHNICAL SERVICE] "
            "Calling Gemini..."
        )


        questions = self.provider.generate_questions(
            request,
            prompt
        )


        if not questions:

            raise RuntimeError(
                "Gemini did not generate any questions."
            )


        print(
            "[TECHNICAL SERVICE] "
            f"Gemini returned {len(questions)} questions."
        )


        # --------------------------------------------------------------
        # Validate and normalize
        # --------------------------------------------------------------

        questions = self._validate_questions(
            questions,
            count
        )


        if not questions:

            raise RuntimeError(
                "No valid questions remained after validation."
            )


        # --------------------------------------------------------------
        # Log count
        # --------------------------------------------------------------

        print(
            "[TECHNICAL SERVICE] "
            f"Valid questions: {len(questions)}"
        )


        if len(questions) != count:

            print(
                "[TECHNICAL SERVICE] WARNING: "
                f"Requested {count}, "
                f"but only {len(questions)} valid questions "
                "were returned."
            )


        # --------------------------------------------------------------
        # Cache
        # --------------------------------------------------------------

        if config.ENABLE_QUESTION_CACHE:

            try:

                self.cache.set(
                    cache_key,
                    questions
                )

            except Exception as e:

                print(
                    "[TECHNICAL SERVICE] "
                    f"Cache write failed: {e}"
                )


        # --------------------------------------------------------------
        # Resume status
        # --------------------------------------------------------------

        if resume_text:

            print(
                "[TECHNICAL SERVICE] "
                "Resume personalization: ENABLED"
            )

            print(
                "[TECHNICAL SERVICE] "
                f"Resume characters: {len(resume_text)}"
            )

        else:

            print(
                "[TECHNICAL SERVICE] "
                "Resume personalization: DISABLED"
            )


        print(
            "[TECHNICAL SERVICE] "
            "Question generation completed."
        )


        return questions


    # ------------------------------------------------------------------
    # Grade Exam
    # ------------------------------------------------------------------

    def grade_exam(
        self,
        session_id,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, Any],
        elapsed_seconds: int,
        time_limit_minutes: int = 10
    ):
        """
        Grade the submitted technical assessment.

        Returns the project's existing ExamResult object.
        """

        from modules.technical.models import ExamResult


        if not questions:

            raise ValueError(
                "No questions available for grading."
            )


        total_questions = len(
            questions
        )


        correct_answers = 0

        wrong_answers = 0

        unanswered = 0


        question_results = []


        # --------------------------------------------------------------
        # Grade each question
        # --------------------------------------------------------------

        for index, question in enumerate(
            questions
        ):

            question_number = index + 1


            correct_option = str(
                question.get(
                    "correct_option",
                    ""
                )
            ).strip().upper()


            # ----------------------------------------------------------
            # Find submitted answer
            # ----------------------------------------------------------

            selected_answer = None


            possible_keys = [
                f"q{question_number}",
                str(question_number),
                f"question_{question_number}",
                f"answer_{question_number}"
            ]


            for key in possible_keys:

                if key in user_answers:

                    selected_answer = (
                        user_answers.get(
                            key
                        )
                    )

                    break


            if selected_answer is not None:

                selected_answer = str(
                    selected_answer
                ).strip().upper()


            # ----------------------------------------------------------
            # Determine result
            # ----------------------------------------------------------

            if not selected_answer:

                status = "unanswered"

                unanswered += 1


            elif selected_answer == correct_option:

                status = "correct"

                correct_answers += 1


            else:

                status = "wrong"

                wrong_answers += 1


            question_results.append(
                {
                    "question_number": question_number,

                    "question": question.get(
                        "question",
                        ""
                    ),

                    "selected_answer": selected_answer,

                    "correct_answer": correct_option,

                    "status": status,

                    "explanation": question.get(
                        "explanation",
                        ""
                    )
                }
            )


        # --------------------------------------------------------------
        # Score
        # --------------------------------------------------------------

        score = correct_answers


        percentage = 0.0


        if total_questions:

            percentage = (
                correct_answers
                / total_questions
            ) * 100


        percentage = round(
            percentage,
            2
        )


        # --------------------------------------------------------------
        # Time
        # --------------------------------------------------------------

        elapsed_seconds = max(
            0,
            int(elapsed_seconds)
        )


        time_limit_seconds = (
            time_limit_minutes * 60
        )


        time_exceeded = (
            elapsed_seconds
            > time_limit_seconds
        )


        minutes = elapsed_seconds // 60

        seconds = elapsed_seconds % 60


        time_taken = (
            f"{minutes}m {seconds}s"
        )


        # --------------------------------------------------------------
        # Performance
        # --------------------------------------------------------------

        if percentage >= 80:

            performance = "Excellent"

        elif percentage >= 60:

            performance = "Good"

        elif percentage >= 40:

            performance = "Average"

        else:

            performance = "Needs Improvement"


        # --------------------------------------------------------------
        # Create ExamResult
        # --------------------------------------------------------------

        try:

            result = ExamResult(
                session_id=session_id,

                total_questions=total_questions,

                correct_answers=correct_answers,

                wrong_answers=wrong_answers,

                unanswered=unanswered,

                score=score,

                percentage=percentage,

                elapsed_seconds=elapsed_seconds,

                time_taken=time_taken,

                time_limit_minutes=time_limit_minutes,

                time_exceeded=time_exceeded,

                performance=performance,

                question_results=question_results
            )


        except TypeError:

            # ----------------------------------------------------------
            # Your existing models.py may have an older ExamResult
            # definition. In that case create it using the core fields.
            # ----------------------------------------------------------

            result = ExamResult(
                session_id=session_id,

                total_questions=total_questions,

                correct_answers=correct_answers,

                wrong_answers=wrong_answers,

                unanswered=unanswered,

                score=score,

                percentage=percentage,

                elapsed_seconds=elapsed_seconds,

                time_taken=time_taken,

                time_limit_minutes=time_limit_minutes,

                time_exceeded=time_exceeded
            )


            # Add extra information if the model permits it.

            try:

                result.performance = performance

                result.question_results = (
                    question_results
                )

            except Exception:

                pass


        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------

        print(
            "[TECHNICAL SERVICE] "
            "Assessment graded."
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Total: {total_questions}"
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Correct: {correct_answers}"
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Wrong: {wrong_answers}"
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Unanswered: {unanswered}"
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Score: {percentage}%"
        )

        print(
            f"[TECHNICAL SERVICE] "
            f"Performance: {performance}"
        )


        return result


# ----------------------------------------------------------------------
# Global service instance
# ----------------------------------------------------------------------

technical_service = TechnicalService()