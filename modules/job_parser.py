"""
job_parser.py
--------------
Parses a pasted job description to extract required skills/keywords,
so the question generator can build job-specific interview questions
(separate from the resume-based and company-placement-bank paths).
"""

import re

# Same keyword universe as resume_parser, extended with a few more general
# software/analyst terms commonly found in job descriptions.
JD_SKILL_KEYWORDS = [
    "python", "java", "c++", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "django", "flask", "spring boot", "sql", "mysql", "postgresql", "mongodb",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "data analysis", "data visualization", "power bi", "tableau", "excel", "aws", "azure",
    "gcp", "docker", "kubernetes", "ci/cd", "git", "rest api", "microservices", "agile",
    "communication", "leadership", "problem solving", "html", "css",
]

ROLE_KEYWORDS = {
    "AIML": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch"],
    "Web Development": ["react", "angular", "vue", "node.js", "django", "flask", "html", "css", "rest api"],
    "Data Science": ["data analysis", "data visualization", "power bi", "tableau", "sql", "excel"],
}


def extract_jd_skills(jd_text: str) -> list:
    text_lower = jd_text.lower()
    return sorted({kw for kw in JD_SKILL_KEYWORDS if kw in text_lower})


def infer_domain_from_jd(jd_text: str) -> str:
    """Best-effort guess of which technical domain this JD belongs to,
    based on which domain's keyword set has the most matches."""
    text_lower = jd_text.lower()
    scores = {domain: sum(1 for kw in kws if kw in text_lower) for domain, kws in ROLE_KEYWORDS.items()}
    best_domain = max(scores, key=scores.get)
    return best_domain if scores[best_domain] > 0 else "Web Development"


def extract_job_title(jd_text: str) -> str:
    """Best-effort extraction of a job title from the first non-empty line."""
    for line in jd_text.strip().splitlines():
        line = line.strip()
        if line and len(line) < 80:
            return re.sub(r"^(job title|role|position)\s*[:\-]\s*", "", line, flags=re.IGNORECASE)
    return "the role"


def build_jd_questions(jd_text: str, skills: list, job_title: str) -> list:
    questions = [f"This role is for {job_title} -- what about it interests you most?"]
    for skill in skills[:4]:
        questions.append(f"The job description mentions {skill}. Can you describe your hands-on experience with it?")
    return questions


def parse_job_description(jd_text: str) -> dict:
    skills = extract_jd_skills(jd_text)
    domain = infer_domain_from_jd(jd_text)
    job_title = extract_job_title(jd_text)
    return {
        "skills": skills,
        "domain": domain,
        "job_title": job_title,
        "questions": build_jd_questions(jd_text, skills, job_title),
    }
