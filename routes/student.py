from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from utils.helpers import student_required
from services.lab_service import get_student_labs, get_lab_by_id
from services.submission_service import submit_lab, get_student_submissions
from services.attendance_service import get_student_attendance
from services.semester_service import get_semester_status
from services.ai_service import generate_mcqs, solve_doubt

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
@student_required
def dashboard():
    user_id = session["user_id"]
    labs = get_student_labs(user_id)
    attendance = get_student_attendance(user_id)
    semester_status = get_semester_status(user_id)
    return render_template("student/dashboard.html", labs=labs, attendance=attendance, semester_status=semester_status)

@student_bp.route("/lab/<lab_id>")
@student_required
def lab_view(lab_id):
    user_id = session["user_id"]
    lab = get_lab_by_id(lab_id)
    submissions = get_student_submissions(user_id, lab_id)
    return render_template("student/lab_view.html", lab=lab, submissions=submissions)

@student_bp.route("/lab/<lab_id>/submit", methods=["POST"])
@student_required
def submit(lab_id):
    user_id = session["user_id"]
    code = request.form.get("code")
    result = submit_lab(user_id, lab_id, code)
    return jsonify(result)

@student_bp.route("/missed-labs")
@student_required
def missed_labs():
    user_id = session["user_id"]
    attendance = get_student_attendance(user_id)
    missed = [a for a in attendance if a["status"] == "Absent"]
    return render_template("student/missed_labs.html", missed=missed)

@student_bp.route("/progress")
@student_required
def progress():
    user_id = session["user_id"]
    semester_status = get_semester_status(user_id)
    submissions = get_student_submissions(user_id)
    return render_template("student/progress.html", semester_status=semester_status, submissions=submissions)

@student_bp.route("/ask-ai")
@student_required
def ask_ai():
    user_id = session["user_id"]
    labs = get_student_labs(user_id)
    return render_template("student/ask_ai.html", labs=labs)

@student_bp.route("/ask-ai/mcq", methods=["POST"])
@student_required
def mcq():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid or missing JSON body."}), 400
    result = generate_mcqs(data.get("lab_id"), data.get("num_questions"), data.get("difficulty"))
    return jsonify(result)

@student_bp.route("/ask-ai/doubt", methods=["POST"])
@student_required
def doubt():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid or missing JSON body."}), 400
    result = solve_doubt(data.get("lab_id"), data.get("question"))
    return jsonify(result)