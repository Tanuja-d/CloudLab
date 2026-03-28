from extensions import mongo
from bson import ObjectId


def get_student_labs(user_id):
    student = mongo.db.students.find_one({"_id": ObjectId(user_id)})
    if not student:
        return {"compulsory": [], "practice": [], "missed": []}

    semester = student["semester"]
    all_labs = list(mongo.db.labs.find({"semester": semester}))

    submissions = {str(s["lab_id"]): s for s in mongo.db.submissions.find({"student_id": user_id})}
    attendance = {str(a["lab_id"]): a for a in mongo.db.attendance.find({"student_id": user_id})}

    compulsory = []
    practice = []
    missed = []

    for lab in all_labs:
        lab["_id"] = str(lab["_id"])
        lab["submission"] = submissions.get(lab["_id"])
        lab["attendance"] = attendance.get(lab["_id"])

        if attendance.get(lab["_id"], {}).get("status") == "Absent":
            missed.append(lab)
        elif lab["type"] == "compulsory":
            compulsory.append(lab)
        elif lab["type"] == "practice":
            practice.append(lab)

    return {"compulsory": compulsory, "practice": practice, "missed": missed}


def get_lab_by_id(lab_id):
    lab = mongo.db.labs.find_one({"_id": ObjectId(lab_id)})
    if lab:
        lab["_id"] = str(lab["_id"])
    return lab


def get_all_labs():
    labs = list(mongo.db.labs.find())
    for lab in labs:
        lab["_id"] = str(lab["_id"])
    return labs


def get_labs_by_semester(semester):
    labs = list(mongo.db.labs.find({"semester": int(semester)}))
    for lab in labs:
        lab["_id"] = str(lab["_id"])
    return labs


def create_lab(data):
    title = data.get("title")
    problem_statement = data.get("problem_statement")
    semester = data.get("semester")
    lab_type = data.get("type")
    expected_output = data.get("expected_output", "")
    content = data.get("content", "")
    deadline = data.get("deadline", "")

    if not all([title, problem_statement, semester, lab_type]):
        return {"success": False, "message": "All required fields must be filled"}

    mongo.db.labs.insert_one({
        "title": title,
        "problem_statement": problem_statement,
        "semester": int(semester),
        "type": lab_type,
        "expected_output": expected_output,
        "content": content,
        "deadline": deadline
    })

    return {"success": True, "message": "Lab created successfully"}


def get_students_for_lab(lab_id):
    lab = mongo.db.labs.find_one({"_id": ObjectId(lab_id)})
    if not lab:
        return []
    semester = lab.get("semester")
    students = list(mongo.db.students.find({"semester": semester}))
    for s in students:
        s["_id"] = str(s["_id"])
        s.pop("password", None)
    return students