"""
modules/technical/routes.py
----------------------------
Flask Blueprint for Technical MCQ Interview Module.
Handles test configuration, question rendering, submission, and result display.
"""

import time
from flask import Blueprint, render_template, request, redirect, url_for, session
from modules.technical.technical_service import technical_service
from modules.technical.models import QuestionRequest
import database

technical_bp = Blueprint("technical", __name__)


def get_current_user():
    user_id = session.get("user_id")
    return database.get_user_by_id(user_id) if user_id else None


@technical_bp.route("/technical", methods=["GET"])
def index():
    """Displays technical test setup page."""
    user = get_current_user()
    from modules.question_bank import COMPANY_LIST
    domains = ["AIML", "Web Development", "Data Science", "Software Engineering", "HR"]
    return render_template("technical.html", domains=domains, company_list=COMPANY_LIST, user=user)


@technical_bp.route("/technical/start", methods=["POST"])
def start():
    """Generates technical questions and initializes test session."""
    company = request.form.get("company", "").strip()
    domain = request.form.get("domain", "").strip()
    difficulty = request.form.get("difficulty", "Medium").strip()
    question_count_raw = request.form.get("question_count", "15")

    try:
        count = int(question_count_raw)
    except (ValueError, TypeError):
        count = 15

    mode = "company" if company else "domain"

    req = QuestionRequest(
        mode=mode,
        domain=domain if domain else None,
        company=company if company else None,
        difficulty=difficulty if difficulty else "Medium",
        count=count
    )

    questions = technical_service.generate_exam_questions(req)

    session["technical_questions"] = questions
    session["technical_start_time"] = time.time()
    session["technical_config"] = {
        "mode": mode,
        "company": company,
        "domain": domain,
        "difficulty": difficulty,
        "count": count
    }

    return redirect(url_for("technical.mcq"))


@technical_bp.route("/technical/mcq", methods=["GET"])
def mcq():
    """Displays MCQ exam interface."""
    questions = session.get("technical_questions")
    if not questions:
        return redirect(url_for("technical.index"))

    user = get_current_user()
    config = session.get("technical_config", {})
    return render_template("mcq.html", questions=questions, user=user, config=config)


@technical_bp.route("/technical/submit", methods=["POST"])
def submit():
    """Evaluates submitted MCQ answers and redirects to results."""
    questions = session.get("technical_questions")
    if not questions:
        return redirect(url_for("technical.index"))

    start_time = session.get("technical_start_time", time.time())
    elapsed_seconds = max(1, int(time.time() - start_time))

    user_answers = dict(request.form)

    session_id = session.get("user_id", 1)

    grading_result = technical_service.grade_exam(
        session_id=session_id,
        questions=questions,
        user_answers=user_answers,
        elapsed_seconds=elapsed_seconds,
        time_limit_minutes=10
    )

    session["technical_result"] = grading_result.to_dict()
    return redirect(url_for("technical.result"))


@technical_bp.route("/technical/result", methods=["GET"])
def result():
    """Displays exam grading results and analytics."""
    result_data = session.get("technical_result")
    if not result_data:
        return redirect(url_for("technical.index"))

    user = get_current_user()
    config = session.get("technical_config", {})
    return render_template("result.html", result=result_data, config=config, user=user)
