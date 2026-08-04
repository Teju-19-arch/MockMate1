"""
modules/technical/ai_provider.py
--------------------------------
Abstract Base Class for AI Question Providers.
Establishes the contract for MCQ generation so Gemini can be swapped
or mocked without altering upstream business logic or routes.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from modules.technical.models import QuestionRequest


class BaseAIProvider(ABC):
    """
    Abstract interface for AI Providers generating technical MCQ questions.
    """

    @abstractmethod
    def generate_questions(self, request: QuestionRequest, prompt: str) -> List[Dict[str, Any]]:
        """
        Generates raw question data dictionaries based on request context and prompt.

        Args:
            request (QuestionRequest): Domain/Company, difficulty, and question count context.
            prompt (str): Constructed prompt from PromptBuilder.

        Returns:
            List[Dict[str, Any]]: List of question dictionaries containing:
                - question: str
                - options: Dict[str, str] (keys 'A', 'B', 'C', 'D')
                - correct_option: str ('A', 'B', 'C', or 'D')
                - explanation: str
        """
        pass
