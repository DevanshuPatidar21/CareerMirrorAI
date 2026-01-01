import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.1-8b-instant"

# --- HELPER: CLEAN JSON ---
def clean_json_response(response_text):
    # Kabhi kabhi AI text ke beech me JSON deta hai, usse extract karne ke liye
    try:
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(response_text)
    except:
        return []

# --- 1. GENERATE APTITUDE MCQs (FIXED: INDEX BASED) ---
def generate_aptitude_questions(role, company, count):
    prompt = f"""
    Generate {count} multiple-choice questions (MCQs) for a placement test.
    Target Role: {role}
    Target Company: {company}
    Topics: Logical Reasoning, Quantitative Aptitude, Technical Basics.
    
    OUTPUT FORMAT: strictly JSON Array.
    Format:
    [
        {{
            "id": 1,
            "q": "Question text?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_index": 0 
        }}
    ]
    IMPORTANT: 
    - "correct_index" must be an integer (0 for the first option, 1 for second, etc).
    - Do NOT use strings for the correct answer, ONLY the index.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7
        )
        return clean_json_response(response.choices[0].message.content)
    except Exception as e:
        print(f"Error Gen MCQs: {e}")
        return []

# --- 2. GENERATE CODING QUESTIONS (Round 2) ---
def generate_coding_questions(role, company, count):
    prompt = f"""
    Generate {count} coding/DSA problem statements for Round 2 of a placement test.
    Target Role: {role}
    Target Company: {company}
    Difficulty: Mix of Easy and Medium.
    
    OUTPUT FORMAT: Strictly return a RAW JSON Array.
    Format:
    [
        {{
            "id": 1,
            "title": "Problem Title",
            "desc": "Detailed problem description...",
            "example_in": "Input example",
            "example_out": "Output example"
        }},
        ...
    ]
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7
        )
        return clean_json_response(response.choices[0].message.content)
    except Exception as e:
        print(f"Error Gen Code Qs: {e}")
        return []

# --- 3. EVALUATE CODE SUBMISSION ---
def evaluate_code_submission(problem_desc, user_code):
    prompt = f"""
    Act as a Technical Interviewer. Evaluate this code.
    
    Problem: {problem_desc}
    User Code:
    ```
    {user_code}
    ```
    
    Task:
    1. Check for correctness logic.
    2. Check for syntax errors.
    3. Rate logic out of 10.
    4. Provide 1-line feedback.
    
    Output JSON:
    {{
        "score": 8,
        "status": "Correct/Partially Correct/Incorrect",
        "feedback": "Logic is good but time complexity is O(n^2)."
    }}
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.2 # Lower temperature for precise grading
        )
        # Parse simple JSON output (handle potential text wrapping)
        txt = response.choices[0].message.content
        if "{" in txt and "}" in txt:
             return json.loads(txt[txt.find("{"):txt.rfind("}")+1])
        return {"score": 0, "status": "Error", "feedback": "AI Eval Failed"}
    except Exception as e:
        return {"score": 0, "status": "Error", "feedback": str(e)}

# --- 4. FINAL ANALYSIS ---
def generate_test_analysis(r1_score, r1_total, r2_feedback_list):
    prompt = f"""
    Generate a final placement test report.
    Round 1 (Aptitude): Scored {r1_score}/{r1_total}.
    Round 2 (Coding): Feedback List -> {r2_feedback_list}
    
    Output format: Markdown.
    Include:
    1. Overall Verdict (Selected/Rejected) based on holistic view.
    2. Strengths.
    3. Areas of Improvement (Specific topics).
    4. Study Plan for next 1 week.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7
        )
        return response.choices[0].message.content
    except:
        return "Analysis could not be generated."