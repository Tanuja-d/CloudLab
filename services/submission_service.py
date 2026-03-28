from extensions import mongo
from bson import ObjectId
from bson.errors import InvalidId
from services.evaluation_service import evaluate_code


def submit_lab(user_id, lab_id, code):
    if not code or not code.strip():
        return {"success": False, "message": "Code cannot be empty"}

    try:
        lab_oid = ObjectId(lab_id)
    except InvalidId:
        return {"success": False, "message": "Invalid lab."}

    lab = mongo.db.labs.find_one({"_id": lab_oid})
    if not lab:
        return {"success": False, "message": "Lab not found"}

    # Count previous attempts by this student for this lab
    attempt_number = mongo.db.submissions.count_documents(
        {"student_id": user_id, "lab_id": lab_id}
    ) + 1

    # AI evaluation
    result = evaluate_code(
        problem_statement=lab.get("problem_statement", ""),
        expected_output=lab.get("expected_output", ""),
        submitted_code=code,
        attempt_number=attempt_number
    )

    ai_score = result.get("score", 0)

    submission = {
        "student_id": user_id,
        "lab_id": lab_id,
        "code": code,
        "gemini_score": ai_score,   # original AI score, never overwritten
        "score": ai_score,          # current score (can be overridden by faculty)
        "status": result.get("status", "Fail"),
        "feedback": result.get("feedback", ""),
        "correctness": result.get("correctness", "Incorrect"),
        "attempt_number": attempt_number,
        "faculty_reviewed": False
    }

    inserted = mongo.db.submissions.insert_one(submission)

    # If student was absent and now submits, update attendance to virtual
    attendance = mongo.db.attendance.find_one(
        {"student_id": user_id, "lab_id": lab_id}
    )
    if attendance and attendance.get("status") == "Absent":
        mongo.db.attendance.update_one(
            {"student_id": user_id, "lab_id": lab_id},
            {"$set": {"status": "Present (Virtual)"}}
        )

    return {
        "success": True,
        "message": "Submission evaluated successfully",
        "submission_id": str(inserted.inserted_id),
        "score": ai_score,
        "status": result.get("status", "Fail"),
        "feedback": result.get("feedback", ""),
        "correctness": result.get("correctness", "Incorrect"),
        "attempt": attempt_number
    }


def get_student_submissions(user_id, lab_id=None):
    query = {"student_id": user_id}
    if lab_id:
        query["lab_id"] = lab_id

    submissions = list(mongo.db.submissions.find(query).sort("attempt_number", 1))
    for s in submissions:
        s["_id"] = str(s["_id"])
        # alias for templates
        s["attempt"] = s.get("attempt_number", 1)
        lab = mongo.db.labs.find_one({"_id": ObjectId(s["lab_id"])})
        s["lab_title"] = lab["title"] if lab else "Unknown"
    return submissions


def get_all_submissions(lab_id=None, semester=None):
    query = {}
    if lab_id:
        query["lab_id"] = lab_id

    # Filter by semester: find lab IDs belonging to that semester first
    if semester:
        labs_in_semester = mongo.db.labs.find({"semester": int(semester)})
        lab_ids = [str(lab["_id"]) for lab in labs_in_semester]
        query["lab_id"] = {"$in": lab_ids}

    submissions = list(mongo.db.submissions.find(query).sort("attempt_number", 1))
    for s in submissions:
        s["_id"] = str(s["_id"])
        # alias for templates
        s["attempt"] = s.get("attempt_number", 1)
        # gemini_score fallback for old records that may not have it
        if "gemini_score" not in s:
            s["gemini_score"] = s.get("score", 0)

        student = mongo.db.students.find_one({"_id": ObjectId(s["student_id"])})
        s["student_name"] = student["name"] if student else "Unknown"
        s["student_id_display"] = student["student_id"] if student else "Unknown"

        lab = mongo.db.labs.find_one({"_id": ObjectId(s["lab_id"])})
        s["lab_title"] = lab["title"] if lab else "Unknown"

    return submissions


def update_submission_score(submission_id, score, feedback):
    if score is None:
        return {"success": False, "message": "Score is required"}

    try:
        score = int(score)
    except (ValueError, TypeError):
        return {"success": False, "message": "Score must be a number"}

    status = "Pass" if score >= 60 else "Fail"

    mongo.db.submissions.update_one(
        {"_id": ObjectId(submission_id)},
        {"$set": {
            "score": score,
            "status": status,
            "feedback": feedback or "",
            "faculty_reviewed": True
        }}
    )

    return {"success": True, "message": "Submission score updated successfully"}
