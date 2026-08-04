"""
modules/technical/mcq_engine.py
-------------------------------
MCQ Business Engine for Technical Interview Evaluation.
Handles answer grading, score calculation, accuracy percentage,
time efficiency metrics, and topic performance analysis.
"""

from typing import List, Dict, Any, Optional
from modules.technical.models import GradingResult, QuestionReview
from modules.technical.utils import calculate_accuracy_percentage, format_seconds_to_mmss


class MCQEngine:
    """
    Evaluates candidate responses for a technical MCQ test.
    """

    MARKS_PER_QUESTION = 10

    @staticmethod
    def evaluate_exam(
        session_id: int,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, str],
        elapsed_seconds: int,
        total_time_limit_minutes: int = 10
    ) -> GradingResult:
        """
        Evaluates submitted candidate answers against correct question options.

        Args:
            session_id (int): Database or tracking ID of the session.
            questions (List[Dict[str, Any]]): Formatted questions list.
            user_answers (Dict[str, str]): Map of question index string ("0", "1", ...) or Q ID -> choice ("A", "B", "C", "D").
            elapsed_seconds (int): Total seconds spent on exam.
            total_time_limit_minutes (int): Allotted exam duration.

        Returns:
            GradingResult: Aggregated evaluation and analytics.
        """
        total_questions = len(questions)
        correct_count = 0
        question_reviews: List[QuestionReview] = []

        for idx, q in enumerate(questions):
            # Resolve user's submitted answer (keyed by string index or question ID)
            user_ans = user_answers.get(str(idx), user_answers.get(f"q_{idx}"))
            if user_ans:
                user_ans = str(user_ans).strip().upper()

            correct_option = str(q.get("correct_option", "A")).strip().upper()
            is_correct = (user_ans == correct_option)

            if is_correct:
                correct_count += 1

            review_item = QuestionReview(
                question_text=q.get("question", ""),
                options=q.get("options", {}),
                user_answer=user_ans,
                correct_option=correct_option,
                is_correct=is_correct,
                explanation=q.get("explanation", "")
            )
            question_reviews.append(review_item)

        # 1. Score calculations
        score = correct_count * MCQEngine.MARKS_PER_QUESTION
        total_marks = total_questions * MCQEngine.MARKS_PER_QUESTION
        accuracy = calculate_accuracy_percentage(correct_count, total_questions)

        # 2. Time efficiency analysis
        time_analytics = MCQEngine._analyze_time(elapsed_seconds, total_time_limit_minutes, total_questions)

        # 3. Performance feedback synthesis
        performance_analytics = MCQEngine._synthesize_analytics(
            correct_count, total_questions, accuracy, time_analytics
        )

        return GradingResult(
            session_id=session_id,
            total_questions=total_questions,
            correct_count=correct_count,
            score=score,
            total_marks=total_marks,
            accuracy_percentage=accuracy,
            time_taken_seconds=elapsed_seconds,
            analytics=performance_analytics,
            question_reviews=question_reviews
        )

    @staticmethod
    def _analyze_time(elapsed_seconds: int, limit_minutes: int, total_questions: int) -> Dict[str, Any]:
        """Calculates time management metrics and pace indicators."""
        allowed_seconds = limit_minutes * 60
        avg_seconds_per_question = round(elapsed_seconds / max(1, total_questions), 1)

        if elapsed_seconds <= (allowed_seconds * 0.5):
            pace_assessment = "Fast Pace (Completed well within allotted time)"
        elif elapsed_seconds <= allowed_seconds:
            pace_assessment = "Optimal Pace (Balanced time distribution)"
        else:
            pace_assessment = "Overtime (Exceeded time limit)"

        return {
            "time_taken_formatted": format_seconds_to_mmss(elapsed_seconds),
            "allowed_time_formatted": format_seconds_to_mmss(allowed_seconds),
            "avg_seconds_per_question": avg_seconds_per_question,
            "pace_assessment": pace_assessment
        }

    @staticmethod
    def _synthesize_analytics(
        correct_count: int,
        total_questions: int,
        accuracy: float,
        time_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates qualitative assessment and action plan based on accuracy."""
        if accuracy >= 80.0:
            level = "Advanced"
            recommendation = "Excellent performance! Focus on complex algorithms and system design edge cases."
        elif accuracy >= 60.0:
            level = "Intermediate"
            recommendation = "Good foundational knowledge. Review explanation feedback on incorrect answers to refine accuracy."
        else:
            level = "Needs Improvement"
            recommendation = "Revise core concepts and practice additional domain MCQs before attempting live placement drives."

        return {
            "readiness_level": level,
            "recommendation": recommendation,
            "time_analytics": time_analytics
        }
