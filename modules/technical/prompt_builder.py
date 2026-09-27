"""
modules/technical/prompt_builder.py
-----------------------------------
Builds prompts for personalized technical MCQs.
"""

from modules.technical.models import QuestionRequest


class PromptBuilder:

    @staticmethod
    def build_prompt(
        request: QuestionRequest,
        resume_text: str = None
    ) -> str:

        mode = request.mode

        domain = request.domain or "Core CS"

        company = request.company or "General IT Placement"

        difficulty = request.difficulty

        count = request.count

        # ---------------------------------------------------------
        # Assessment context
        # ---------------------------------------------------------

        if mode == "company":

            assessment_context = f"""
The candidate is preparing for a technical placement
assessment associated with {company}.

Generate company-oriented placement preparation
questions, but DO NOT claim that the questions are
actual or leaked questions from {company}.
"""

        else:

            assessment_context = f"""
The candidate selected the technical domain:

{domain}

The questions must evaluate knowledge relevant to
this domain.
"""

        # ---------------------------------------------------------
        # Resume context
        # ---------------------------------------------------------

        if resume_text:

            # Limit prompt size while retaining enough resume
            # information for personalization.
            resume_for_prompt = resume_text[:15000]

            resume_context = f"""
CANDIDATE RESUME
================

{resume_for_prompt}

RESUME-BASED QUESTION REQUIREMENTS
==================================

Use the candidate's resume as a major source for
personalizing the technical assessment.

Identify relevant technologies such as:

- Programming languages
- Frameworks
- Libraries
- Databases
- AI/ML technologies
- APIs
- Cloud technologies
- DevOps tools
- Development tools
- Projects
- Technical skills
- Architecture concepts

If the resume contains projects, generate questions
about the technologies, algorithms, architecture,
databases, APIs, models, or implementation concepts
used in those projects.

Do not simply copy sentences from the resume.

Test whether the candidate actually understands
the technologies mentioned in the resume.
"""

        else:

            resume_context = """
No resume text was available.

Generate questions only from the selected
domain/company and difficulty.
"""

        # ---------------------------------------------------------
        # Final prompt
        # ---------------------------------------------------------

        prompt = f"""
You are an expert technical interviewer and
computer science examiner.

TASK
====

Generate exactly {count} multiple-choice technical
questions for this assessment.

ASSESSMENT MODE:
{mode}

SELECTED DOMAIN:
{domain}

SELECTED COMPANY:
{company}

DIFFICULTY:
{difficulty}

{assessment_context}

{resume_context}

DIFFICULTY GUIDELINES
=====================

Easy:
- Fundamentals
- Definitions
- Basic syntax
- Simple conceptual questions

Medium:
- Concept application
- Code tracing
- Practical scenarios
- APIs
- Data structures
- Database concepts
- ML concepts

Hard:
- Optimization
- Edge cases
- Architecture
- Complex algorithms
- Internal mechanisms
- Advanced technical reasoning

QUESTION RULES
==============

1. Generate exactly {count} questions.

2. Every question must have exactly four options.

3. Options must be labelled:
   A
   B
   C
   D

4. Exactly ONE option must be correct.

5. Questions must be technically accurate.

6. Avoid duplicate questions.

7. Questions should be personalized using
   the candidate's resume wherever relevant.

8. Combine resume technologies with the selected
   domain or company.

9. Do not ask questions about personal information
   unrelated to technical skills.

10. Do not invent technologies that are not present
    in the resume unless they are required by the
    selected domain.

11. For projects in the resume, test understanding
    of implementation and technical decisions.

12. Provide a short explanation for the correct answer.

13. Do not include markdown.

14. Return ONLY valid JSON.

OUTPUT FORMAT
=============

{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_option": "A",
            "explanation": "Short explanation."
        }}
    ]
}}
"""

        return prompt.strip()