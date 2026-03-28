from functools import wraps
from flask import session, redirect, url_for, flash


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "student":
            flash("Please login as a student to continue")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def faculty_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "faculty":
            flash("Please login as faculty to continue")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def format_datetime(dt_string):
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return dt_string


def calculate_progress(passed, total):
    if total == 0:
        return 0
    return round((passed / total) * 100, 2)