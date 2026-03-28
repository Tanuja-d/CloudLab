from extensions import mongo
from bson import ObjectId


def mark_attendance(data):
    records = data.get("records", [])
    if not records:
        return {"success": False, "message": "No records provided"}

    for record in records:
        student_id = record.get("student_id")
        lab_id = record.get("lab_id")
        status = record.get("status")

        existing = mongo.db.attendance.find_one({"student_id": student_id, "lab_id": lab_id})
        if existing:
            mongo.db.attendance.update_one(
                {"student_id": student_id, "lab_id": lab_id},
                {"$set": {"status": status}}
            )
        else:
            mongo.db.attendance.insert_one({
                "student_id": student_id,
                "lab_id": lab_id,
                "status": status
            })

    return {"success": True, "message": "Attendance marked successfully"}


def get_student_attendance(user_id):
    records = list(mongo.db.attendance.find({"student_id": user_id}))
    for r in records:
        r["_id"] = str(r["_id"])
        lab = mongo.db.labs.find_one({"_id": ObjectId(r["lab_id"])})
        r["lab_title"] = lab["title"] if lab else "Unknown"
    return records


def get_attendance_by_lab(lab_id):
    records = list(mongo.db.attendance.find({"lab_id": lab_id}))
    for r in records:
        r["_id"] = str(r["_id"])
        student = mongo.db.students.find_one({"_id": ObjectId(r["student_id"])})
        r["student_name"] = student["name"] if student else "Unknown"
        r["student_id_display"] = student["student_id"] if student else "Unknown"
    return records


def update_attendance_to_virtual(student_id, lab_id):
    mongo.db.attendance.update_one(
        {"student_id": student_id, "lab_id": lab_id},
        {"$set": {"status": "Present (Virtual)"}}
    )