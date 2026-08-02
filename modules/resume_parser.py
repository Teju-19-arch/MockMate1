"""
resume_parser.py
-----------------
Extracts raw text from an uploaded PDF/DOCX resume and pulls out
skills, so the question generator can build resume-aware questions.
"""

import re
import io
import docx
from PyPDF2 import PdfReader

# A small reference skill vocabulary per domain. In a production build,
# swap this for a proper NLP entity extractor (e.g. spaCy NER + a skills
# taxonomy) -- this keyword approach is intentionally simple and fast.
SKILL_KEYWORDS = {
    "AIML": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp",
             "computer vision", "scikit-learn", "keras", "opencv", "pandas", "numpy"],
    "Web Development": ["react", "node.js", "javascript", "html", "css", "django",
                         "flask", "mongodb", "sql", "rest api", "typescript", "express"],
    "Data Science": ["pandas", "numpy", "sql", "tableau", "power bi", "statistics",
                      "data visualization", "r programming", "excel", "etl"],
    "HR": ["communication", "leadership", "recruitment", "team management",
           "conflict resolution", "negotiation"],
}


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from an uploaded PDF or DOCX file (given as bytes)."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif filename.lower().endswith(".docx"):
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in document.paragraphs)
    else:
        raise ValueError("Unsupported resume format. Please upload a PDF or DOCX file.")


def extract_skills(resume_text: str, domain: str = None) -> list:
    """Return the list of known skills found in the resume text.
    If a domain is given, only that domain's keyword list is checked;
    otherwise every domain's keywords are checked."""
    text_lower = resume_text.lower()
    domains_to_check = [domain] if domain and domain in SKILL_KEYWORDS else SKILL_KEYWORDS.keys()

    found = set()
    for d in domains_to_check:
        for skill in SKILL_KEYWORDS[d]:
            if skill in text_lower:
                found.add(skill)
    return sorted(found)


def extract_projects_section(resume_text: str) -> str:
    """Best-effort extraction of the 'Projects' section from a resume,
    used to tailor a couple of resume-specific interview questions."""
    match = re.search(
        r"(projects?|academic projects?)\s*[:\n](.+?)(?=\n[A-Z][a-zA-Z ]{2,20}\n|$)",
        resume_text,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(2).strip()[:800] if match else ""


def parse_resume(file_bytes: bytes, filename: str, domain: str = None) -> dict:
    """Convenience wrapper used by app.py: does the full parse in one call."""
    text = extract_text(file_bytes, filename)
    return {
        "raw_text": text,
        "skills": extract_skills(text, domain),
        "projects_excerpt": extract_projects_section(text),
    }
