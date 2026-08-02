"""
question_generator.py
-----------------------
Builds the final interview question set for a session from one of
three modes:
  1. domain      - generic HR + technical questions for a chosen domain
  2. company     - a specific company's campus placement question bank
  3. job         - questions tailored to a pasted job description
Resume-based questions are layered on top in all three modes when a
resume was uploaded.
"""

from modules import question_bank, job_parser


def build_resume_questions(skills: list, projects_excerpt: str) -> list:
    questions = []
    for skill in skills[:2]:
        questions.append(f"I see you've worked with {skill}. Can you walk me through a project where you used it?")
    if projects_excerpt:
        questions.append(
            "Tell me more about one of the projects listed on your resume -- what was your specific contribution?"
        )
    return questions


def generate_questions(mode: str, domain: str = None, company: str = None, jd_text: str = None,
                        resume_skills: list = None, projects_excerpt: str = "") -> dict:
    """
    mode: "domain" | "company" | "job"
    Returns {"questions": [...], "meta": {...}} where meta carries any
    inferred info (e.g. jd-inferred domain) useful for the UI/report.
    """
    resume_skills = resume_skills or []
    questions = []
    meta = {}

    if mode == "company" and company:
        questions.extend(question_bank.get_company_questions(company))
        meta["company"] = company

    elif mode == "job" and jd_text:
        parsed = job_parser.parse_job_description(jd_text)
        questions.extend(question_bank.get_hr_questions(2))
        questions.extend(question_bank.get_technical_questions(parsed["domain"], 3))
        questions.extend(parsed["questions"])
        meta.update(parsed)

    else:  # domain mode (default)
        domain = domain or "Web Development"
        questions.extend(question_bank.get_hr_questions(3))
        questions.extend(question_bank.get_technical_questions(domain, 3))
        meta["domain"] = domain

    questions.extend(build_resume_questions(resume_skills, projects_excerpt))

    return {"questions": questions, "meta": meta}
