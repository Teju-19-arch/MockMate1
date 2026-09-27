"""
database.py
------------
SQLite persistence for MockMate: users, interview sessions (now aware of
target company / job description / domain), and per-answer reports.
"""

import sqlite3
import os
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "mockmate.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            college TEXT,
            branch TEXT,
            target_role TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,              -- 'domain' | 'company' | 'job'
            domain TEXT,
            company TEXT,
            job_title TEXT,
            resume_filename TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            transcript TEXT,
            filler_word_count INTEGER,
            speaking_rate_wpm REAL,
            pause_count INTEGER,
            eye_contact_score REAL,
            confidence_score REAL,
            overall_score REAL,
            feedback TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def create_user(name, email, password, college="", branch="", target_role=""):
    conn = get_connection()
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        cur.execute(
            """INSERT INTO users (name, email, password_hash, college, branch, target_role, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, email, password_hash, college, branch, target_role, datetime.now().isoformat()),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return dict(row)
    return None


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def create_session(user_id, mode, domain=None, company=None, job_title=None, resume_filename=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sessions (user_id, mode, domain, company, job_title, resume_filename, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, mode, domain, company, job_title, resume_filename, datetime.now().isoformat()),
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return session_id


def get_session(session_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_report(session_id, question, analysis):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reports (
                session_id, question, transcript, filler_word_count, speaking_rate_wpm,
                pause_count, eye_contact_score, confidence_score, overall_score, feedback, created_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            question,
            analysis.get("transcript", ""),
            analysis.get("filler_word_count", 0),
            analysis.get("speaking_rate_wpm", 0.0),
            analysis.get("pause_count", 0),
            analysis.get("eye_contact_score", 0.0),
            analysis.get("confidence_score", 0.0),
            analysis.get("overall_score", 0.0),
            analysis.get("feedback", ""),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_session_reports(session_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE session_id = ? ORDER BY id", (session_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_session_summary(session_id):
    """Aggregates every answer in one interview session into a single
    overall report, shown once at the end of the interview instead of
    per-question."""
    reports = get_session_reports(session_id)
    if not reports:
        return {
            "total_questions": 0,
            "avg_overall": 0.0,
            "avg_eye_contact": 0.0,
            "avg_confidence": 0.0,
            "avg_wpm": 0.0,
            "total_filler_words": 0,
            "total_pauses": 0,
            "combined_feedback": [],
            "per_question": [],
        }

    total = len(reports)
    avg_overall = round(sum(r["overall_score"] for r in reports) / total, 1)
    avg_eye = round(sum(r["eye_contact_score"] for r in reports) / total, 1)
    avg_conf = round(sum(r["confidence_score"] for r in reports) / total, 1)
    avg_wpm = round(sum(r["speaking_rate_wpm"] for r in reports) / total, 1)
    total_filler = sum(r["filler_word_count"] for r in reports)
    total_pauses = sum(r["pause_count"] for r in reports)

    # De-duplicated list of feedback tips seen across all answers.
    combined_feedback = []
    for r in reports:
        for tip in (r.get("feedback") or "").split(". "):
            tip = tip.strip().rstrip(".")
            if tip and tip not in combined_feedback:
                combined_feedback.append(tip)

    return {
        "total_questions": total,
        "avg_overall": avg_overall,
        "avg_eye_contact": avg_eye,
        "avg_confidence": avg_conf,
        "avg_wpm": avg_wpm,
        "total_filler_words": total_filler,
        "total_pauses": total_pauses,
        "combined_feedback": combined_feedback,
        "per_question": reports,
    }


def get_user_progress(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT r.*, s.domain, s.company, s.job_title, s.mode, s.created_at as session_date
           FROM reports r
           JOIN sessions s ON r.session_id = s.id
           WHERE s.user_id = ?
           ORDER BY r.created_at DESC""",
        (user_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_readiness_summary(user_id):
    """Aggregates report history into dashboard-friendly stats:
    overall readiness score, per-company average, sessions completed."""
    reports = get_user_progress(user_id)
    if not reports:
        return {
            "total_answers": 0,
            "avg_overall": 0,
            "avg_eye_contact": 0,
            "avg_confidence": 0,
            "by_company": {},
        }

    total = len(reports)
    avg_overall = round(sum(r["overall_score"] for r in reports) / total, 1)
    avg_eye = round(sum(r["eye_contact_score"] for r in reports) / total, 1)
    avg_conf = round(sum(r["confidence_score"] for r in reports) / total, 1)

    by_company = {}
    for r in reports:
        if r.get("company"):
            by_company.setdefault(r["company"], []).append(r["overall_score"])
    by_company_avg = {c: round(sum(v) / len(v), 1) for c, v in by_company.items()}

    return {
        "total_answers": total,
        "avg_overall": avg_overall,
        "avg_eye_contact": avg_eye,
        "avg_confidence": avg_conf,
        "by_company": by_company_avg,
    }