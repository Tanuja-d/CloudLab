import google.generativeai as genai
from config import Config
from extensions import mongo
from bson import ObjectId
import json, re

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.GEMINI_MODEL)


def get_lab_content(lab_id):
    lab = mongo.db.labs.find_one({"_id": ObjectId(lab_id)})
    if not lab:
        return None
    return lab.get("content") or lab.get("problem_statement") or ""


def generate_mcqs(lab_id, num_questions, difficulty):
    content = get_lab_content(lab_id)
    if not content:
        return {"success": False, "message": "Lab content not found"}

    num_questions = int(num_questions) if num_questions else 5
    difficulty = difficulty if difficulty in ["easy", "medium", "hard"] else "medium"

    prompt = f"""
You are an expert engineering professor generating MCQ questions for a lab session.

Lab Content:
{content}

Generate {num_questions} MCQ questions at {difficulty} difficulty level.

Respond in the following JSON format only, no extra text:
{{
    "questions": [
        {{
            "question": "<question text>",
            "options": ["A. <option>", "B. <option>", "C. <option>", "D. <option>"],
            "correct_answer": "<A or B or C or D>",
            "explanation": "<brief explanation>"
        }}
    ]
}}
"""
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean up any potential markdown formatting
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    text = text.strip()
    
    try:
        parsed = json.loads(text)
        return {"success": True, "data": parsed}
    except json.JSONDecodeError:
        # Fallback to regex if standard parsing fails
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return {"success": True, "data": parsed}
            except json.JSONDecodeError:
                pass
                
    return {"success": False, "message": "Failed to generate MCQs. Please retry."}


def solve_doubt(lab_id, question):
    content = get_lab_content(lab_id)
    if not content:
        return {"success": False, "message": "Lab content not found"}

    if not question or not question.strip():
        return {"success": False, "message": "Question cannot be empty"}

    prompt = f"""
You are a helpful lab assistant for engineering students.

Lab Material:
{content}

Student Question:
{question}

Answer the question strictly based on the provided lab material only.
If the answer is not found in the lab material, respond with: "Not found in lab material."

Respond in the following JSON format only:
{{
    "answer": "<clear answer>",
    "explanation": "<step-by-step explanation if applicable>",
    "found_in_material": <true or false>
}}
"""
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean up any potential markdown formatting
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    text = text.strip()
    
    try:
        parsed = json.loads(text)
        return {"success": True, "data": parsed}
    except json.JSONDecodeError:
        # Fallback to regex if standard parsing fails
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return {"success": True, "data": parsed}
            except json.JSONDecodeError:
                pass

    return {"success": False, "message": "Failed to process your question. Please retry."}