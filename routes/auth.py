from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from services.auth_service import signup_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    return render_template("index.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        result = signup_user(data)
        if result["success"]:
            flash(result["message"])
            return redirect(url_for("auth.login"))
        flash(result["message"])
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        result = login_user(data)
        if result["success"]:
            session["user_id"] = result["user_id"]
            session["role"] = result["role"]
            session["name"] = result["name"]
            if result["role"] == "student":
                return redirect(url_for("student.dashboard"))
            return redirect(url_for("faculty.dashboard"))
        flash(result["message"])
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))