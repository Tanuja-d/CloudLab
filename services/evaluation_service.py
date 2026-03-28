import json
import re

import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.GEMINI_MODEL)

_MAX_FIELD = 80_000


def _clip(text, limit=_MAX_FIELD):
    if not text:
        return ""
    text = str(text)
    if len(text) > limit:
        return text[:limit] + "\n[Truncated for evaluation.]"
    return text


def _gemini_response_text(response):
    try:
        return response.text
    except (ValueError, AttributeError):
        return None


def evaluate_code(problem_statement, expected_output, submitted_code, attempt_number):
    problem_statement = _clip(problem_statement)
    expected_output = _clip(expected_output)
    submitted_code = _clip(submitted_code, limit=50_000)

    prompt = f"""
You are a strict lab evaluator for an engineering college virtual lab system.

Problem Statement:
{problem_statement}

Expected Output:
{expected_output}

Student Submitted Code:
{submitted_code}

Attempt Number: {attempt_number}

Evaluate the submitted code strictly. Respond in the following JSON format only:
{{
    "score": <integer between 0 and 100>,
    "status": "<Pass or Fail>",
    "feedback": "<clear explanation of what is correct and what is wrong>",
    "correctness": "<Correct / Partially Correct / Incorrect>"
}}

Scoring rules:
- Correct output on attempt 1: 90-100
- Correct output on attempt 2: 75-89
- Correct output on attempt 3+: 60-74
- Partially correct: 30-59
- Incorrect: 0-29
- Pass if score >= 60
"""
    try:
        response = model.generate_content(prompt)
    except Exception:
        return {
            "score": 0,
            "status": "Fail",
            "feedback": "AI evaluation failed. Check GEMINI_API_KEY and GEMINI_MODEL on the server, or try again later.",
            "correctness": "Incorrect",
        }

    text = _gemini_response_text(response)
    if not text or not text.strip():
        return {
            "score": 0,
            "status": "Fail",
            "feedback": "AI returned no evaluation (blocked or empty). Please try again.",
            "correctness": "Incorrect",
        }
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return {
        "score": 0,
        "status": "Fail",
        "feedback": "Could not parse AI evaluation. Please retry.",
        "correctness": "Incorrect",
    }
