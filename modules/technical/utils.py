"""
modules/technical/utils.py
---------------------------
Reusable helper and utility functions for Technical Interview Module.
Handles string sanitization, prefix stripping, time formatting,
and mathematical accuracy calculations.
"""

import re
import uuid
from typing import Dict


def sanitize_text(text: str) -> str:
    """Removes trailing/leading whitespace and normalizes unprintable control chars."""
    if not text:
        return ""
    # Replace non-breaking spaces and redundant whitespaces
    cleaned = text.replace("\xa0", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def clean_option_text(option_text: str) -> str:
    """Strips leading option prefixes such as 'A)', 'A.', '(A)', 'a)', or 'A:'."""
    if not option_text:
        return ""
    text = str(option_text).strip()
    # Match patterns like "A)", "A.", "(A)", "A:", "a)" at the beginning of option strings
    pattern = r"^\s*(?:\([A-Da-d]\)|[A-Da-d][\.\)\:\-]|Option\s+[A-Da-d][\:\.\)]?)\s*"
    cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return cleaned.strip()


def normalize_options(options: Dict[str, str]) -> Dict[str, str]:
    """Ensures options dict has upper-case keys ('A','B','C','D') with sanitized values."""
    normalized = {}
    for key, value in options.items():
        clean_key = str(key).strip().upper()
        if clean_key in ("A", "B", "C", "D"):
            normalized[clean_key] = clean_option_text(value)
    return normalized


def format_seconds_to_mmss(total_seconds: int) -> str:
    """Formats an integer seconds count into MM:SS string display."""
    minutes = max(0, total_seconds // 60)
    seconds = max(0, total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def calculate_accuracy_percentage(correct_count: int, total_count: int) -> float:
    """Calculates accuracy percentage rounded to 1 decimal place."""
    if total_count <= 0:
        return 0.0
    return round((correct_count / total_count) * 100.0, 1)


def generate_session_uuid() -> str:
    """Generates a unique random string token for exam tracking."""
    return uuid.uuid4().hex
