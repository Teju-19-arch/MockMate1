"""
app.py
-------
MockMate: Intelligent Interview Preparation System (Flask edition)
Live webcam/mic interview recording, AI avatar delivering questions,
and placement-focused dashboard (job-description mode + company-wise
campus placement mode).

Run with: python app.py
"""

import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

import database
from modules import resume_parser, job_parser, question_generator, speech_analyzer, facial_analyzer, report_generator
from modules.question_bank import COMPANY_LIST

app = Flask(__name__)
app.secret_key = "mockmate-dev-secret-change-this-in-production"

BASE_DIR = os.path.dirname(__file__)
TEMP_UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

DOMAINS = ["AIML", "Web Development", "Data Science", "HR"]

database.init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def current_user():
    user_id = session.get("user_id")
    return database.get_user_by_id(user_id) if user_id else None


def login_required(view):
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("dashboard") if current_user() else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        college = request.form.get("college", "")
        branch = request.form.get("branch", "")
        target_role = request.form.get("target_role", "")

        user_id = database.create_user(name, email, password, college, branch, target_role)
        if user_id:
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("That email is already registered.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = database.authenticate_user(email, password)
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    summary = database.get_readiness_summary(user["id"])
    history = database.get_user_progress(user["id"])[:10]
    return render_template(
        "dashboard.html", user=user, summary=summary, history=history,
        company_list=COMPANY_LIST,
    )


# ---------------------------------------------------------------------------
# New interview setup
# ---------------------------------------------------------------------------

@app.route("/new-interview", methods=["GET", "POST"])
@login_required
def new_interview():
    user = current_user()

    if request.method == "POST":
        mode = request.form["mode"]  # 'domain' | 'company' | 'job'
        domain = request.form.get("domain")
        company = request.form.get("company")
        jd_text = request.form.get("job_description", "")

        resume_file = request.files.get("resume")
        resume_skills, projects_excerpt, resume_filename = [], "", None
        if resume_file and resume_file.filename:
            file_bytes = resume_file.read()
            parsed = resume_parser.parse_resume(file_bytes, resume_file.filename, domain)
            resume_skills = parsed["skills"]
            projects_excerpt = parsed["projects_excerpt"]
            resume_filename = resume_file.filename

        result = question_generator.generate_questions(
            mode=mode, domain=domain, company=company, jd_text=jd_text,
            resume_skills=resume_skills, projects_excerpt=projects_excerpt,
        )
        questions = result["questions"]
        meta = result["meta"]

        session_id = database.create_session(
            user_id=user["id"],
            mode=mode,
            domain=meta.get("domain", domain),
            company=company,
            job_title=meta.get("job_title"),
            resume_filename=resume_filename,
        )

        # Stash the generated questions for the interview room page.
        session[f"questions_{session_id}"] = questions
        return redirect(url_for("interview_room", session_id=session_id))

    return render_template("new_interview.html", domains=DOMAINS, company_list=COMPANY_LIST)


# ---------------------------------------------------------------------------
# Live interview room (AI avatar + webcam recording)
# ---------------------------------------------------------------------------

@app.route("/interview/<int:session_id>")
@login_required
def interview_room(session_id):
    interview_session = database.get_session(session_id)
    if not interview_session or interview_session["user_id"] != current_user()["id"]:
        flash("Interview session not found.", "error")
        return redirect(url_for("dashboard"))

    questions = session.get(f"questions_{session_id}", [])
    return render_template(
        "interview_room.html", session_id=session_id, questions=questions,
        interview_session=interview_session,
    )


@app.route("/api/analyze/<int:session_id>", methods=["POST"])
@login_required
def api_analyze(session_id):
    interview_session = database.get_session(session_id)
    if not interview_session or interview_session["user_id"] != current_user()["id"]:
        return jsonify({"error": "Session not found"}), 404

    question = request.form.get("question", "")
    media_file = request.files.get("media")
    if not media_file:
        return jsonify({"error": "No media uploaded"}), 400

    unique_name = f"{uuid.uuid4().hex}.webm"
    save_path = os.path.join(TEMP_UPLOAD_DIR, unique_name)
    media_file.save(save_path)

    try:
        speech_result = speech_analyzer.analyze_speech(save_path)
        facial_result = facial_analyzer.analyze_video(save_path)
        analysis = report_generator.build_report(speech_result, facial_result)
        database.save_report(session_id, question, analysis)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up temp media -- we only persist the extracted scores/transcript, not raw video.
        if os.path.exists(save_path):
            os.remove(save_path)
        converted = save_path.rsplit(".", 1)[0] + "_converted.wav"
        if os.path.exists(converted):
            os.remove(converted)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
