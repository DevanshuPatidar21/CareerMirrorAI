import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ API Key Missing! Check .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# 🔥 USING THE FASTEST & NEWEST MODEL
MODEL_NAME = 'gemini-2.5-flash'

def get_gemini_response_safe(prompt):
    """
    Smart Wrapper: Handles Rate Limits (429) automatically.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    for attempt in range(3): # Try 3 times before giving up
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                time.sleep(5) # Wait 5s if quota hits
                continue
            return f"Error: {str(e)}"
    return "⚠️ Server is busy. Please try again."

def generate_interview_question(role, topic, difficulty, resume_text="", company_name="General"):
    prompt = f"""
    Act as a Senior Technical Recruiter for {company_name}.
    Role: {role}
    Topic: {topic}
    Difficulty: {difficulty}
    Candidate's Resume Snippet: "{resume_text[:1000]}"
    
    Task: Generate ONE sharp, technical interview question relevant to the resume and topic.
    Constraint: Do not provide the answer. Just the question.
    """
    return get_gemini_response_safe(prompt)

def analyze_answer(question, user_answer):
    prompt = f"""
    You are evaluating a candidate.
    Question: {question}
    Candidate Answer: {user_answer}
    
    Task: Analyze using the STAR method.
    Output Format (Markdown):
    * **Rating:** ⭐ [Score/10]
    * **Feedback:** [Brief Strength analysis]
    * **Improvement Tip:** [One actionable technical correction]
    """
    return get_gemini_response_safe(prompt)