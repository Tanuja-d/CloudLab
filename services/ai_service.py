import google.generativeai as genai
from config import Config
from extensions import mongo
from bson import ObjectId
from bson.errors import InvalidId
import json, re

MAX_LAB_CHARS_FOR_AI = 120_000

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.GEMINI_MODEL)


def _gemini_response_text(response):
    try:
        return response.text
    except (ValueError, AttributeError):
        return None


def get_lab_content(lab_id):
    if not lab_id or not isinstance(lab_id, str):
        return None
    try:
        oid = ObjectId(lab_id)
    except InvalidId:
        return None
    lab = mongo.db.labs.find_one({"_id": oid})
    if not lab:
        return None
    raw = lab.get("content") or lab.get("problem_statement") or ""
    if not raw:
        return None
    if len(raw) > MAX_LAB_CHARS_FOR_AI:
        raw = raw[:MAX_LAB_CHARS_FOR_AI] + "\n\n[Truncated for AI — lab content was very long.]"
    return raw


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
    try:
        response = model.generate_content(prompt)
    except Exception:
        return {
            "success": False,
            "message": "AI request failed. Check GEMINI_API_KEY and GEMINI_MODEL on the server, or try again later.",
        }

    text = _gemini_response_text(response)
    if not text or not text.strip():
        return {
            "success": False,
            "message": "The AI returned no text (blocked or empty). Try a different lab or shorten lab content.",
        }
    text = text.strip()
    
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
    try:
        response = model.generate_content(prompt)
    except Exception:
        return {
            "success": False,
            "message": "AI request failed. Check GEMINI_API_KEY and GEMINI_MODEL on the server, or try again later.",
        }

    text = _gemini_response_text(response)
    if not text or not text.strip():
        return {
            "success": False,
            "message": "The AI returned no text (blocked or empty). Try again or rephrase your question.",
        }
    text = text.strip()
    
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