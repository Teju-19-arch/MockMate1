"""
modules/technical/models.py
----------------------------
Shared data models for the Technical Interview Module.
Defines strongly-typed dataclasses for request contexts,
MCQ questions, session details, and grading results.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class MCQQuestion:
    """Represents a single Multiple Choice Question."""
    question: str
    options: Dict[str, str]  # Keyed by 'A', 'B', 'C', 'D'
    correct_option: str       # 'A', 'B', 'C', or 'D'
    explanation: str
    id: Optional[int] = None

    def to_dict(self, include_correct: bool = True) -> dict:
        """Converts to dictionary format for JSON serialization."""
        data = {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "explanation": self.explanation if include_correct else "",
        }
        if include_correct:
            data["correct_option"] = self.correct_option
        return data


@dataclass
class QuestionRequest:
    """Encapsulates parameters required to generate technical questions."""
    mode: str                         # 'domain' or 'company'
    domain: Optional[str] = None
    company: Optional[str] = None
    difficulty: str = "Medium"        # 'Easy', 'Medium', 'Hard'
    count: int = 15
    time_limit_minutes: int = 10

    def cache_key(self) -> str:
        """Generates a deterministic string key for caching identical requests."""
        target = self.company if self.mode == "company" else self.domain
        return f"{self.mode}:{target}:{self.difficulty}:{self.count}".lower()


@dataclass
class QuestionReview:
    """Detailed review item for a single question after grading."""
    question_text: str
    options: Dict[str, str]
    user_answer: Optional[str]
    correct_option: str
    is_correct: bool
    explanation: str


@dataclass
class GradingResult:
    """Aggregated test evaluation metrics and performance analytics."""
    session_id: int
    total_questions: int
    correct_count: int
    score: int
    total_marks: int
    accuracy_percentage: float
    time_taken_seconds: int
    analytics: Dict[str, any] = field(default_factory=dict)
    question_reviews: List[QuestionReview] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Converts grading result into a serializable dict."""
        return {
            "session_id": self.session_id,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": self.score,
            "total_marks": self.total_marks,
            "accuracy_percentage": self.accuracy_percentage,
            "time_taken_seconds": self.time_taken_seconds,
            "analytics": self.analytics,
            "question_reviews": [asdict(r) for r in self.question_reviews],
        }
