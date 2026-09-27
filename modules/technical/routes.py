"""
modules/technical/routes.py
---------------------------

Flask Blueprint for the Technical MCQ Interview Module.

Features:
- Domain-wise technical assessment
- Company placement assessment
- Optional resume upload
- PDF/DOCX resume extraction
- Resume-personalized Gemini questions
- Server-side assessment storage
- MCQ rendering
- Answer submission
- Result display
"""

import time
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from modules.technical.technical_service import technical_service
from modules.technical.models import QuestionRequest
from modules.technical.resume_parser import extract_resume_text

import database


# ============================================================================
# BLUEPRINT
# ============================================================================

technical_bp = Blueprint(
    "technical",
    __name__
)


# ============================================================================
# SERVER-SIDE ASSESSMENT STORAGE
# ============================================================================

"""
The questions and resume text are stored here instead of inside
the Flask session.

This prevents the Flask session cookie from becoming too large.
"""

TECHNICAL_ASSESSMENTS = {}


# ============================================================================
# CURRENT USER
# ============================================================================

def get_current_user():

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        return None

    return database.get_user_by_id(
        user_id
    )


# ============================================================================
# TECHNICAL ASSESSMENT SETUP PAGE
# ============================================================================

@technical_bp.route(
    "/technical",
    methods=["GET"]
)
def index():

    user = get_current_user()

    from modules.question_bank import COMPANY_LIST

    domains = [
        "AIML",
        "Web Development",
        "Data Science",
        "Software Engineering",
        "HR"
    ]

    return render_template(
        "technical.html",
        domains=domains,
        company_list=COMPANY_LIST,
        user=user
    )


# ============================================================================
# START TECHNICAL ASSESSMENT
# ============================================================================

@technical_bp.route(
    "/technical/start",
    methods=["POST"]
)
def start():

    # ------------------------------------------------------------------------
    # Remove old technical assessment information
    # ------------------------------------------------------------------------

    session.pop(
        "technical_questions",
        None
    )

    session.pop(
        "technical_assessment_id",
        None
    )

    session.pop(
        "technical_start_time",
        None
    )

    session.pop(
        "technical_config",
        None
    )

    session.pop(
        "technical_result",
        None
    )

    session.pop(
        "technical_result_config",
        None
    )


    # ------------------------------------------------------------------------
    # Read form values
    # ------------------------------------------------------------------------

    company = request.form.get(
        "company",
        ""
    ).strip()

    domain = request.form.get(
        "domain",
        ""
    ).strip()

    difficulty = request.form.get(
        "difficulty",
        "Medium"
    ).strip()

    question_count_raw = request.form.get(
        "question_count",
        "15"
    ).strip()

    selected_mode = request.form.get(
        "mode",
        "domain"
    ).strip().lower()


    # ------------------------------------------------------------------------
    # Question count
    # ------------------------------------------------------------------------

    try:

        count = int(
            question_count_raw
        )

    except (
        ValueError,
        TypeError
    ):

        count = 15


    if count < 1:

        count = 15


    if count > 20:

        count = 20


    # ------------------------------------------------------------------------
    # Determine assessment mode
    # ------------------------------------------------------------------------

    if selected_mode == "company":

        mode = "company"

        if not company:

            flash(
                "Please select a company.",
                "error"
            )

            return redirect(
                url_for(
                    "technical.index"
                )
            )

        # Company mode does not use domain.
        domain = ""

    else:

        mode = "domain"

        if not domain:

            flash(
                "Please select a technical domain.",
                "error"
            )

            return redirect(
                url_for(
                    "technical.index"
                )
            )

        # Domain mode does not use company.
        company = ""


    # ------------------------------------------------------------------------
    # OPTIONAL RESUME
    # ------------------------------------------------------------------------

    resume_file = request.files.get(
        "resume"
    )

    resume_text = ""

    resume_filename = None


    # ------------------------------------------------------------------------
    # If a resume was uploaded, process it.
    #
    # If no resume was uploaded, simply continue.
    # ------------------------------------------------------------------------

    if resume_file and resume_file.filename:

        resume_filename = (
            resume_file.filename
        )

        print(
            "[TECHNICAL] Resume upload detected."
        )

        print(
            f"[TECHNICAL] Resume filename: "
            f"{resume_filename}"
        )


        try:

            resume_text = extract_resume_text(
                resume_file
            )

        except ValueError as e:

            print(
                f"[TECHNICAL] Resume validation error: {e}"
            )

            flash(
                str(e),
                "error"
            )

            return redirect(
                url_for(
                    "technical.index"
                )
            )

        except Exception as e:

            print(
                "[TECHNICAL] Resume extraction failed: "
                f"{e}"
            )

            flash(
                "Unable to process the uploaded resume. "
                "Please check the file and try again.",
                "error"
            )

            return redirect(
                url_for(
                    "technical.index"
                )
            )


        print(
            "[TECHNICAL] Resume text extracted: "
            f"{len(resume_text)} characters"
        )

    else:

        print(
            "[TECHNICAL] No resume uploaded."
        )

        print(
            "[TECHNICAL] Continuing without "
            "resume personalization."
        )


    # ------------------------------------------------------------------------
    # Build QuestionRequest
    # ------------------------------------------------------------------------

    req = QuestionRequest(
        mode=mode,

        domain=(
            domain
            if domain
            else None
        ),

        company=(
            company
            if company
            else None
        ),

        difficulty=(
            difficulty
            or "Medium"
        ),

        count=count
    )


    # ------------------------------------------------------------------------
    # Debug information
    # ------------------------------------------------------------------------

    print(
        "=================================================="
    )

    print(
        "[TECHNICAL] Starting Technical Assessment"
    )

    print(
        f"[TECHNICAL] Mode: {mode}"
    )

    print(
        f"[TECHNICAL] Domain: {domain}"
    )

    print(
        f"[TECHNICAL] Company: {company}"
    )

    print(
        f"[TECHNICAL] Difficulty: {difficulty}"
    )

    print(
        f"[TECHNICAL] Question count: {count}"
    )

    print(
        f"[TECHNICAL] Resume provided: "
        f"{'YES' if resume_text else 'NO'}"
    )

    print(
        "=================================================="
    )


    # ------------------------------------------------------------------------
    # Generate questions
    # ------------------------------------------------------------------------

    try:

        questions = technical_service.generate_exam_questions(
            req,
            resume_text=resume_text
        )

    except Exception as e:

        print(
            "[TECHNICAL] Question generation failed:"
        )

        print(
            repr(e)
        )

        flash(
            f"Unable to generate technical questions: {e}",
            "error"
        )

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Make sure questions exist
    # ------------------------------------------------------------------------

    if not questions:

        flash(
            "No technical questions were generated. "
            "Please try again.",
            "error"
        )

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Check generated count
    # ------------------------------------------------------------------------

    if len(questions) != count:

        print(
            "[TECHNICAL] WARNING:"
        )

        print(
            f"[TECHNICAL] Requested {count} questions, "
            f"received {len(questions)}."
        )


    # ------------------------------------------------------------------------
    # Generate unique assessment ID
    # ------------------------------------------------------------------------

    assessment_id = str(
        uuid.uuid4()
    )


    # ------------------------------------------------------------------------
    # Assessment configuration
    # ------------------------------------------------------------------------

    assessment_config = {

        "mode": mode,

        "company": company,

        "domain": domain,

        "difficulty": difficulty,

        "count": count,

        "resume_filename": resume_filename

    }


    # ------------------------------------------------------------------------
    # Store assessment server-side
    # ------------------------------------------------------------------------

    TECHNICAL_ASSESSMENTS[
        assessment_id
    ] = {

        "questions": questions,

        "resume_text": resume_text,

        "config": assessment_config,

        "created_at": time.time(),

        "user_id": session.get(
            "user_id",
            1
        )

    }


    # ------------------------------------------------------------------------
    # Store ONLY small values in session
    # ------------------------------------------------------------------------

    session[
        "technical_assessment_id"
    ] = assessment_id


    session[
        "technical_start_time"
    ] = time.time()


    session.modified = True


    # ------------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------------

    print(
        "[TECHNICAL] Assessment created:"
    )

    print(
        f"[TECHNICAL] Assessment ID: "
        f"{assessment_id}"
    )

    print(
        f"[TECHNICAL] Questions generated: "
        f"{len(questions)}"
    )

    print(
        f"[TECHNICAL] Resume personalization: "
        f"{'ENABLED' if resume_text else 'DISABLED'}"
    )


    # ------------------------------------------------------------------------
    # Redirect to MCQ page
    # ------------------------------------------------------------------------

    return redirect(
        url_for(
            "technical.mcq"
        )
    )


# ============================================================================
# MCQ PAGE
# ============================================================================

@technical_bp.route(
    "/technical/mcq",
    methods=["GET"]
)
def mcq():

    assessment_id = session.get(
        "technical_assessment_id"
    )


    print(
        "[TECHNICAL] MCQ requested."
    )

    print(
        f"[TECHNICAL] Assessment ID: "
        f"{assessment_id}"
    )


    # ------------------------------------------------------------------------
    # No assessment ID
    # ------------------------------------------------------------------------

    if not assessment_id:

        print(
            "[TECHNICAL] ERROR: "
            "No assessment ID in session."
        )

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get server-side assessment
    # ------------------------------------------------------------------------

    assessment = TECHNICAL_ASSESSMENTS.get(
        assessment_id
    )


    if not assessment:

        print(
            "[TECHNICAL] ERROR: "
            "Assessment not found."
        )

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get questions
    # ------------------------------------------------------------------------

    questions = assessment.get(
        "questions",
        []
    )


    if not questions:

        print(
            "[TECHNICAL] ERROR: "
            "Assessment contains no questions."
        )

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get configuration
    # ------------------------------------------------------------------------

    assessment_config = assessment.get(
        "config",
        {}
    )


    user = get_current_user()


    print(
        f"[TECHNICAL] Displaying "
        f"{len(questions)} questions."
    )


    # ------------------------------------------------------------------------
    # Render MCQ page
    # ------------------------------------------------------------------------

    return render_template(
        "mcq.html",

        questions=questions,

        user=user,

        config=assessment_config
    )


# ============================================================================
# SUBMIT TECHNICAL ASSESSMENT
# ============================================================================

@technical_bp.route(
    "/technical/submit",
    methods=["POST"]
)
def submit():

    # ------------------------------------------------------------------------
    # Get assessment ID
    # ------------------------------------------------------------------------

    assessment_id = session.get(
        "technical_assessment_id"
    )


    if not assessment_id:

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get assessment
    # ------------------------------------------------------------------------

    assessment = TECHNICAL_ASSESSMENTS.get(
        assessment_id
    )


    if not assessment:

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get questions
    # ------------------------------------------------------------------------

    questions = assessment.get(
        "questions",
        []
    )


    if not questions:

        return redirect(
            url_for(
                "technical.index"
            )
        )


    # ------------------------------------------------------------------------
    # Get configuration
    # ------------------------------------------------------------------------

    assessment_config = assessment.get(
        "config",
        {}
    )


    # ------------------------------------------------------------------------
    # Calculate elapsed time
    # ------------------------------------------------------------------------

    start_time = session.get(
        "technical_start_time",
        time.time()
    )


    elapsed_seconds = max(
        1,
        int(
            time.time()
            - start_time
        )
    )


    # ------------------------------------------------------------------------
    # Get submitted answers
    # ------------------------------------------------------------------------

    user_answers = dict(
        request.form
    )


    # ------------------------------------------------------------------------
    # Current user/session
    # ------------------------------------------------------------------------

    session_id = session.get(
        "user_id",
        1
    )


    # ------------------------------------------------------------------------
    # Grade assessment
    # ------------------------------------------------------------------------

    try:

        grading_result = technical_service.grade_exam(

            session_id=session_id,

            questions=questions,

            user_answers=user_answers,

            elapsed_seconds=elapsed_seconds,

            time_limit_minutes=10

        )

    except Exception as e:

        print(
            "[TECHNICAL] Grading failed:"
        )

        print(
            repr(e)
        )

        flash(
            "Unable to calculate the assessment result.",
            "error"
        )

        return redirect(
            url_for(
                "technical.mcq"
            )
        )


    # ------------------------------------------------------------------------
    # Convert result to dictionary
    # ------------------------------------------------------------------------

    try:

        result_data = (
            grading_result.to_dict()
        )

    except AttributeError:

        # Fallback if the result object does not
        # have a to_dict() method.

        result_data = {

            "session_id": session_id,

            "total_questions": getattr(
                grading_result,
                "total_questions",
                len(questions)
            ),

            "correct_answers": getattr(
                grading_result,
                "correct_answers",
                0
            ),

            "wrong_answers": getattr(
                grading_result,
                "wrong_answers",
                0
            ),

            "unanswered": getattr(
                grading_result,
                "unanswered",
                0
            ),

            "score": getattr(
                grading_result,
                "score",
                0
            ),

            "percentage": getattr(
                grading_result,
                "percentage",
                0
            ),

            "elapsed_seconds": getattr(
                grading_result,
                "elapsed_seconds",
                elapsed_seconds
            ),

            "time_taken": getattr(
                grading_result,
                "time_taken",
                ""
            ),

            "time_limit_minutes": getattr(
                grading_result,
                "time_limit_minutes",
                10
            ),

            "time_exceeded": getattr(
                grading_result,
                "time_exceeded",
                False
            )

        }


    # ------------------------------------------------------------------------
    # Store result in session
    # ------------------------------------------------------------------------

    session[
        "technical_result"
    ] = result_data


    # ------------------------------------------------------------------------
    # Store small configuration
    # ------------------------------------------------------------------------

    session[
        "technical_result_config"
    ] = {

        "mode": assessment_config.get(
            "mode"
        ),

        "company": assessment_config.get(
            "company"
        ),

        "domain": assessment_config.get(
            "domain"
        ),

        "difficulty": assessment_config.get(
            "difficulty"
        ),

        "count": assessment_config.get(
            "count"
        ),

        "resume_filename": assessment_config.get(
            "resume_filename"
        )

    }


    # ------------------------------------------------------------------------
    # Remove completed assessment from server memory
    # ------------------------------------------------------------------------

    TECHNICAL_ASSESSMENTS.pop(
        assessment_id,
        None
    )


    # ------------------------------------------------------------------------
    # Remove assessment-specific session values
    # ------------------------------------------------------------------------

    session.pop(
        "technical_assessment_id",
        None
    )

    session.pop(
        "technical_start_time",
        None
    )


    session.modified = True


    # ------------------------------------------------------------------------
    # Redirect to result page
    # ------------------------------------------------------------------------

    return redirect(
        url_for(
            "technical.result"
        )
    )


# ============================================================================
# RESULT PAGE
# ============================================================================

@technical_bp.route(
    "/technical/result",
    methods=["GET"]
)
def result():

    result_data = session.get(
        "technical_result"
    )


    if not result_data:

        return redirect(
            url_for(
                "technical.index"
            )
        )


    user = get_current_user()


    result_config = session.get(
        "technical_result_config",
        {}
    )


    return render_template(
        "result.html",

        result=result_data,

        config=result_config,

        user=user
    )