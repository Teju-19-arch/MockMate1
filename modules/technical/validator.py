"""
modules/technical/validator.py
-------------------------------
JSON Validation & Structural Verification Layer for AI-generated MCQ questions.
Ensures outputs strictly conform to required schemas before reaching the business engine.
"""

from typing import List, Dict, Any


class JSONValidationError(Exception):
    """Raised when AI provider response fails JSON schema validation."""
    pass


class QuestionValidator:
    """
    Validates structure, keys, option counts, and answer integrity of raw question dicts.
    """

    @staticmethod
    def validate_question_list(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validates a list of question dictionaries.

        Raises:
            JSONValidationError: If any question fails structural or content validation.
        """
        if not isinstance(questions, list) or len(questions) == 0:
            raise JSONValidationError("Expected non-empty list of questions from AI provider.")

        validated_questions = []
        for idx, q in enumerate(questions, start=1):
            validated_q = QuestionValidator.validate_single_question(q, idx)
            validated_questions.append(validated_q)

        return validated_questions

    @staticmethod
    def validate_single_question(q: Dict[str, Any], index: int = 1) -> Dict[str, Any]:
        """
        Validates a single MCQ question dictionary.
        """
        if not isinstance(q, dict):
            raise JSONValidationError(f"Question #{index} is not a valid dictionary object.")

        # 1. Validate Question Text
        question_text = q.get("question")
        if not question_text or not isinstance(question_text, str) or not question_text.strip():
            raise JSONValidationError(f"Question #{index} is missing a valid 'question' text string.")

        # 2. Validate Options Dict
        options = q.get("options")
        if not options or not isinstance(options, dict):
            raise JSONValidationError(f"Question #{index} is missing a valid 'options' dictionary.")

        # Ensure exactly 4 options with keys A, B, C, D
        required_keys = {"A", "B", "C", "D"}
        actual_keys = {str(k).strip().upper() for k in options.keys()}
        if actual_keys != required_keys:
            raise JSONValidationError(
                f"Question #{index} options must contain exactly keys A, B, C, D. Found: {list(options.keys())}"
            )

        # Validate non-empty option text values
        for key in required_keys:
            val = options.get(key)
            if val is None or not str(val).strip():
                raise JSONValidationError(f"Question #{index} option '{key}' has empty text.")

        # 3. Validate Correct Option Choice
        correct_option = q.get("correct_option")
        if not correct_option or not isinstance(correct_option, str):
            raise JSONValidationError(f"Question #{index} is missing 'correct_option'.")

        clean_correct = correct_option.strip().upper()
        if clean_correct not in required_keys:
            raise JSONValidationError(
                f"Question #{index} 'correct_option' must be one of A, B, C, D. Found: '{correct_option}'"
            )

        # 4. Validate Explanation
        explanation = q.get("explanation")
        if not explanation or not isinstance(explanation, str) or not explanation.strip():
            raise JSONValidationError(f"Question #{index} is missing a valid 'explanation' string.")

        return {
            "question": question_text.strip(),
            "options": {str(k).strip().upper(): str(v).strip() for k, v in options.items()},
            "correct_option": clean_correct,
            "explanation": explanation.strip()
        }
