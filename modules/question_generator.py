
"""
question_generator.py
---------------------
Generates interview questions for domain, company, and job modes.

Interview order:
1. Mandatory introduction
2. Easy questions
3. Medium questions
4. Hard questions

Technical domains receive only domain-specific questions.
HR questions are used only for the HR domain.
"""

import random
from modules import question_bank, job_parser


INTRO_QUESTION = "Tell me about yourself."

DOMAIN_ALIASES = {
    "aiml": "AIML",
    "ai/ml": "AIML",
    "ai & ml": "AIML",
    "artificial intelligence": "AIML",
    "artificial intelligence and machine learning": "AIML",
    "machine learning": "AIML",
    "web development": "Web Development",
    "web development domain": "Web Development",
    "web dev": "Web Development",
    "data science": "Data Science",
    "hr": "HR",
    "human resources": "HR",
}


# Keywords used to estimate question difficulty.
# Questions matching advanced keywords are placed later.
HARD_KEYWORDS = (
    "design a scalable",
    "architecture",
    "optimize",
    "optimization",
    "debug",
    "trade-off",
    "tradeoff",
    "production",
    "deployment",
    "monitor",
    "complex",
    "advanced",
    "real-world",
    "real world",
    "improve an existing",
    "reliability",
    "security concerns",
    "multithreading",
    "backpropagation",
    "transformer",
    "attention mechanism",
    "data leakage",
    "class imbalance",
    "hypothesis testing",
    "multicollinearity",
    "dimensionality reduction",
    "window functions",
)

MEDIUM_KEYWORDS = (
    "how would you",
    "how do you",
    "when would you",
    "compare",
    "difference",
    "evaluate",
    "validate",
    "investigate",
    "apply",
    "project",
    "scenario",
    "test and debug",
    "performance",
    "feature engineering",
    "cross-validation",
    "cross validation",
)


def normalize_domain(domain=None):
    """Normalize a domain name to the question-bank key."""
    if not domain:
        return "Web Development"

    cleaned = domain.strip()
    return DOMAIN_ALIASES.get(cleaned.casefold(), cleaned)


def deduplicate_questions(questions):
    """Remove duplicate questions while preserving their order."""
    result = []
    seen = set()

    for question in questions:
        if not isinstance(question, str):
            continue

        question = " ".join(question.split())
        key = question.casefold()

        if question and key not in seen:
            seen.add(key)
            result.append(question)

    return result


def estimate_difficulty(question):
    """
    Estimate difficulty from question wording.

    Returns:
        1 = Easy
        2 = Medium
        3 = Hard

    For precise difficulty levels, store an explicit difficulty
    field alongside each question in question_bank.py.
    """
    text = question.casefold()

    if any(keyword in text for keyword in HARD_KEYWORDS):
        return 3

    if any(keyword in text for keyword in MEDIUM_KEYWORDS):
        return 2

    return 1


def order_questions(questions, mandatory_intro=True):
    """
    Put the mandatory introduction first, then order other
    questions from easy to hard.

    Questions at the same difficulty level are randomized.
    """
    questions = deduplicate_questions(questions)

    remaining = [
        question for question in questions
        if question.casefold() != INTRO_QUESTION.casefold()
    ]

    easy = []
    medium = []
    hard = []

    for question in remaining:
        level = estimate_difficulty(question)

        if level == 1:
            easy.append(question)
        elif level == 2:
            medium.append(question)
        else:
            hard.append(question)

    random.shuffle(easy)
    random.shuffle(medium)
    random.shuffle(hard)

    ordered = easy + medium + hard

    if mandatory_intro:
        return [INTRO_QUESTION] + ordered

    return ordered


def build_resume_questions(skills=None, projects_excerpt=""):
    """Create questions based on resume skills and projects."""
    questions = []

    for skill in (skills or [])[:2]:
        questions.append(
            f"Tell me about a project where you used {skill}."
        )

    if projects_excerpt and projects_excerpt.strip():
        questions.append(
            "Explain your contribution to a project on your resume."
        )

    return questions


def generate_questions(
    mode,
    domain=None,
    company=None,
    jd_text=None,
    resume_skills=None,
    projects_excerpt="",
):
    """
    Return:
        {
            "questions": [...],
            "meta": {...}
        }

    The introduction is always the first question.
    Other questions are ordered from estimated easy to hard.
    """
    mode = (mode or "domain").strip().casefold()
    questions = []
    meta = {}

    # ------------------------------------------------------
    # COMPANY MODE
    # ------------------------------------------------------
    if mode == "company":
        if not company:
            raise ValueError("Please select a company.")

        questions.extend(
            question_bank.get_company_questions(company)
        )
        meta["company"] = company

        if not questions:
            raise ValueError(
                f"No questions found for company: {company}"
            )

    # ------------------------------------------------------
    # JOB DESCRIPTION MODE
    # ------------------------------------------------------
    elif mode == "job":
        if not jd_text or not jd_text.strip():
            raise ValueError("Please provide a job description.")

        parsed = job_parser.parse_job_description(jd_text)
        selected_domain = normalize_domain(
            parsed.get("domain", domain)
        )

        meta.update(parsed)
        meta["domain"] = selected_domain

        questions.extend(
            question_bank.get_technical_questions(
                selected_domain, 10
            )
        )

        questions.extend(parsed.get("questions", []))

    # ------------------------------------------------------
    # GENERAL DOMAIN MODE
    # ------------------------------------------------------
    elif mode == "domain":
        selected_domain = normalize_domain(domain)

        # Only retrieve questions from the selected domain.
        questions.extend(
            question_bank.get_technical_questions(
                selected_domain, 10
            )
        )

        meta["domain"] = selected_domain

    else:
        raise ValueError(f"Unsupported interview mode: {mode}")

    # Add resume-based questions if provided.
    questions.extend(
        build_resume_questions(
            resume_skills,
            projects_excerpt,
        )
    )

    # Ensure the introduction is mandatory and first.
    questions = order_questions(
        questions,
        mandatory_intro=True,
    )

    meta["question_count"] = len(questions)
    meta["difficulty_order"] = ["introduction", "easy", "medium", "hard"]

    return {
        "questions": questions,
        "meta": meta,
    }
