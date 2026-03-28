from extensions import mongo
from bson import ObjectId


def get_semester_status(user_id):
    student = mongo.db.students.find_one({"_id": ObjectId(user_id)})
    if not student:
        return {}

    semester = student["semester"]
    all_labs = list(mongo.db.labs.find({"semester": semester, "type": "compulsory"}))
    total_labs = len(all_labs)

    if total_labs == 0:
        return {
            "semester": semester,
            "total_labs": 0,
            "passed_labs": 0,
            "progress_percent": 0,
            "promoted": False,
            "message": "No labs assigned for this semester yet"
        }

    lab_ids = [str(lab["_id"]) for lab in all_labs]

    passed_submissions = []
    for lab_id in lab_ids:
        best = mongo.db.submissions.find_one(
            {"student_id": user_id, "lab_id": lab_id, "status": "Pass"},
            sort=[("score", -1)]
        )
        if best:
            passed_submissions.append(best)

    passed_count = len(passed_submissions)
    progress_percent = round((passed_count / total_labs) * 100, 2)
    promoted = progress_percent >= 60

    message = (
        f"Semester {semester} Passed — Eligible for Semester {semester + 1}"
        if promoted
        else f"Pending — Complete remaining labs to pass Semester {semester}"
    )

    return {
        "semester": semester,
        "total_labs": total_labs,
        "passed_labs": passed_count,
        "progress_percent": progress_percent,
        "promoted": promoted,
        "message": message
    }