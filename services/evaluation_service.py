import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.GEMINI_MODEL)


def evaluate_code(problem_statement, expected_output, submitted_code, attempt_number):
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

    import json, re
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return {"score": 0, "status": "Fail", "feedback": "Evaluation failed. Please retry.", "correctness": "Incorrect"}