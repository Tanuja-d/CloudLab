from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from utils.helpers import faculty_required
from services.lab_service import get_all_labs, create_lab, get_labs_by_semester, get_students_for_lab
from services.attendance_service import mark_attendance, get_attendance_by_lab
from services.submission_service import get_all_submissions, update_submission_score

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")

@faculty_bp.route("/dashboard")
@faculty_required
def dashboard():
    labs = get_all_labs()
    return render_template("faculty/dashboard.html", labs=labs)

@faculty_bp.route("/assign-labs", methods=["GET", "POST"])
@faculty_required
def assign_labs():
    if request.method == "POST":
        data = request.form
        result = create_lab(data)
        return jsonify(result)
    labs = get_all_labs()
    return render_template("faculty/assign_labs.html", labs=labs)

@faculty_bp.route("/attendance/students")
@faculty_required
def attendance_students():
    lab_id = request.args.get("lab_id")
    students = get_students_for_lab(lab_id) if lab_id else []
    return jsonify({"students": students})

@faculty_bp.route("/attendance", methods=["GET", "POST"])
@faculty_required
def attendance():
    if request.method == "POST":
        data = request.json
        result = mark_attendance(data)
        return jsonify(result)
    lab_id = request.args.get("lab_id")
    attendance_data = get_attendance_by_lab(lab_id) if lab_id else []
    labs = get_all_labs()
    return render_template("faculty/attendance.html", attendance=attendance_data, labs=labs)

@faculty_bp.route("/submissions")
@faculty_required
def submissions():
    lab_id = request.args.get("lab_id")
    semester = request.args.get("semester")
    all_submissions = get_all_submissions(lab_id=lab_id, semester=semester)
    labs = get_all_labs()
    return render_template("faculty/submissions.html", submissions=all_submissions, labs=labs)

@faculty_bp.route("/submissions/<submission_id>/review", methods=["POST"])
@faculty_required
def review_submission(submission_id):
    data = request.json
    result = update_submission_score(submission_id, data.get("score"), data.get("feedback"))
    return jsonify(result)