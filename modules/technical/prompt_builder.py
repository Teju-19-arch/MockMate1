"""
modules/technical/prompt_builder.py
-----------------------------------
Prompt Builder Engine for Technical MCQ Generation.
Constructs structured LLM prompts for Domain-wise and Company-wise placement tests,
supporting multiple languages/technologies and forcing strict JSON output.
"""

from typing import Optional
from modules.technical.models import QuestionRequest

SUPPORTED_TECHNOLOGIES = [
    "Python", "Java", "C", "C++", "AIML", "Web Development",
    "Data Science", "Cloud", "DevOps", "Core CS"
]


class PromptBuilder:
    """
    Constructs optimized prompts for Gemini API to generate technical MCQs.
    """

    @staticmethod
    def build_prompt(request: QuestionRequest) -> str:
        """
        Builds a comprehensive LLM prompt based on QuestionRequest parameters.
        """
        mode = request.mode
        domain = request.domain or "Core CS"
        company = request.company or "IT Company"
        difficulty = request.difficulty
        count = request.count

        if mode == "company":
            context_description = (
                f"a Campus Placement Recruitment Technical Assessment for '{company}'. "
                f"The questions should reflect actual placement drive technical round standards at {company}."
            )
        else:
            context_description = (
                f"a Technical Interview Assessment focusing on '{domain}'. "
                f"The questions must evaluate domain competence in {domain}."
            )

        prompt = f"""
You are an expert technical interviewer and computer science examiner for campus placement recruitment.

TASK:
Generate exactly {count} multiple-choice questions (MCQs) for {context_description}

DIFFICULTY LEVEL: {difficulty}
- Easy: Foundational concepts, syntax, definitions, basic output prediction.
- Medium: Conceptual application, data structures, code snippet tracing, API usage.
- Hard: Optimization, internal mechanics, edge cases, complex algorithms, system design.

REQUIREMENTS:
1. Every question must have EXACTLY 4 distinct option choices labeled "A", "B", "C", and "D".
2. Exactly ONE option must be correct.
3. Provide a clear, educational 1-3 sentence explanation for why the correct option is right.
4. If code snippets are included in the question, format them clearly.

STRICT JSON OUTPUT FORMAT:
Return ONLY a valid JSON object matching the following JSON schema. Do NOT include markdown blocks like ```json, do NOT include intro or outro text.

JSON Schema:
{{
  "questions": [
    {{
      "question": "Clear technical question text here",
      "options": {{
        "A": "First choice option",
        "B": "Second choice option",
        "C": "Third choice option",
        "D": "Fourth choice option"
      }},
      "correct_option": "A",
      "explanation": "Brief explanation of the correct choice."
    }}
  ]
}}
"""
        return prompt.strip()
