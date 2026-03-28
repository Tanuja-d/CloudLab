from extensions import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import re

def signup_user(data):
    role = data.get("role")
    name = data.get("name")
    user_id = data.get("user_id")
    password = data.get("password")

    if not all([role, name, user_id, password]):
        return {"success": False, "message": "All fields are required"}

    if role == "student":
        semester = data.get("semester")
        branch = data.get("branch")
        if not all([semester, branch]):
            return {"success": False, "message": "Semester and branch are required for students"}
        collection = mongo.db.students
        existing = collection.find_one({"student_id": user_id})
        if existing:
            return {"success": False, "message": "Student ID already registered"}
        collection.insert_one({
            "name": name,
            "student_id": user_id,
            "semester": int(semester),
            "branch": branch,
            "password": generate_password_hash(password)
        })

    elif role == "faculty":
        collection = mongo.db.faculty
        existing = collection.find_one({"faculty_id": user_id})
        if existing:
            return {"success": False, "message": "Faculty ID already registered"}
        collection.insert_one({
            "name": name,
            "faculty_id": user_id,
            "password": generate_password_hash(password)
        })

    else:
        return {"success": False, "message": "Invalid role"}

    return {"success": True, "message": "Registration successful. Please login."}


def login_user(data):
    user_id = data.get("user_id")
    password = data.get("password")
    role = data.get("role")

    if not all([user_id, password, role]):
        return {"success": False, "message": "All fields are required"}

    if role == "student":
        user = mongo.db.students.find_one({"student_id": user_id})
    elif role == "faculty":
        user = mongo.db.faculty.find_one({"faculty_id": user_id})
    else:
        return {"success": False, "message": "Invalid role"}

    if not user or not check_password_hash(user["password"], password):
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "user_id": str(user["_id"]),
        "role": role,
        "name": user["name"]
    }