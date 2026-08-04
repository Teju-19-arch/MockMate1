"""
modules/technical/formatter.py
-------------------------------
Question Formatter Layer for Technical Interview Module.
Sanitizes markdown artifacts, strips option prefixes ('A)', 'B.', etc.),
formats code blocks, and standardizes options into clean dictionaries.
"""

import re
from typing import List, Dict, Any
from modules.technical.utils import sanitize_text, clean_option_text


class QuestionFormatter:
    """
    Sanitizes, cleans, and formats raw question structures.
    """

    @staticmethod
    def format_question_list(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats a list of validated question dictionaries.
        """
        formatted_list = []
        for q in questions:
            formatted_list.append(QuestionFormatter.format_single_question(q))
        return formatted_list

    @staticmethod
    def format_single_question(q: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes text, strips option prefixes, and normalizes code formatting for one question.
        """
        raw_question = q.get("question", "")
        raw_options = q.get("options", {})
        raw_correct = q.get("correct_option", "A").strip().upper()
        raw_explanation = q.get("explanation", "")

        # 1. Clean Question Text & Markdown backticks
        clean_question = QuestionFormatter._clean_text_and_markdown(raw_question)

        # 2. Normalize and strip prefixes from options
        clean_options = {}
        for key in ["A", "B", "C", "D"]:
            opt_val = raw_options.get(key, raw_options.get(key.lower(), ""))
            clean_options[key] = clean_option_text(str(opt_val))

        # 3. Clean Explanation Text
        clean_explanation = QuestionFormatter._clean_text_and_markdown(raw_explanation)

        return {
            "question": clean_question,
            "options": clean_options,
            "correct_option": raw_correct,
            "explanation": clean_explanation
        }

    @staticmethod
    def _clean_text_and_markdown(text: str) -> str:
        """
        Removes markdown wrappers (e.g. ```json or stray backticks) while preserving formatted code blocks.
        """
        if not text:
            return ""

        # Remove leading/trailing json codefence wrappers if LLM returned them accidentally
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json|python|html|sql)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Sanitize whitespace
        return sanitize_text(cleaned)
