import os
import uuid
from dotenv import load_dotenv
from groq import Groq
import pyttsx3
import time
import random  # <--- NEW: Randomization ke liye

# 1. SETUP - USING GROQ
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ CRITICAL: GROQ_API_KEY not found in .env file!")

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"❌ Client Init Error: {e}")

MODEL_NAME = "llama-3.1-8b-instant"

def get_groq_response(system_prompt, user_prompt):
    try:
        if not GROQ_API_KEY:
            return "Error: GROQ_API_KEY missing in .env"

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=MODEL_NAME,
            temperature=0.9, # <--- CHANGED: High temperature for more creativity
            max_tokens=150,
            top_p=1,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"API Error: {str(e)}"

# 🔥 FIXED: RANDOM TOPIC GENERATION
def generate_gd_topic():
    # Categories list taki har baar alag flavor mile
    categories = [
        "Artificial Intelligence & Future", 
        "Social Media & Mental Health", 
        "Remote Work vs Office", 
        "Indian Economy & Startups", 
        "Education System & Exams", 
        "Climate Change & EV",
        "Abstract Topics (e.g., Red vs Blue)",
        "Corporate Ethics"
    ]
    selected_cat = random.choice(categories)
    
    sys = "You are a GD Moderator."
    # Prompt ko dynamic bana diya timestamp aur category ke saath
    usr = f"Generate ONE unique, controversial Group Discussion topic about '{selected_cat}'. output ONLY the topic title. Do not give quotes."
    return get_groq_response(sys, usr)

# --- AGENTS (Updated for Stability) ---
def get_piyush_response(topic, history):
    sys = f"""
    You are 'Piyush', a participant in a Group Discussion on '{topic}'.
    Your Role: Assertive but polite team player.
    Instructions:
    1. Listen to the last speaker.
    2. Agree or partially disagree logically.
    3. Speaks VERY BRIEFLY (Max 2 short sentences).
    """
    usr = f"Chat History:\n{history[-1000:]}\n\nYour turn. Respond to the last point briefly."
    return get_groq_response(sys, usr)

def get_anjali_response(topic, history):
    sys = f"""
    You are 'Anjali', a participant in a Group Discussion on '{topic}'.
    Your Role: Calm, supportive, adds new perspectives.
    Instructions:
    1. Acknowledge the last speaker's point.
    2. Add a new dimension or example.
    3. Keep it VERY SHORT (Max 2 sentences).
    """
    usr = f"Chat History:\n{history[-1000:]}\n\nYour turn. Add a quick point."
    return get_groq_response(sys, usr)

def analyze_turn(topic, user_input, history):
    sys = "You are an HR Evaluator observing a GD."
    usr = f"Topic: {topic}. The candidate said: '{user_input}'. Give 1 short line of constructive feedback (Max 15 words)."
    return get_groq_response(sys, usr)

def generate_final_report(topic, chat_history):
    sys = "You are a Senior HR Interviewer."
    usr = f"""
    Evaluate the candidate ('You') based on this GD Transcript:
    Topic: {topic}
    {chat_history}
    
    Task: Generate a markdown report.
    Format:
    ### 📊 Performance Score: [X/10]
    **✅ Strong Points:** [List]
    **⚠️ Areas of Improvement:** [List]
    **🏆 Best Quote:** [Quote]
    """
    return get_groq_response(sys, usr)

# --- TTS ENGINE (FIXED: ENGINE LOCK ISSUE) ---
def text_to_speech(text, gender="Male"):
    try:
        if not text or "Error" in text: return None
        
        clean_text = text.replace("Piyush:", "").replace("Anjali:", "").replace("*", "").replace('"', "").replace("#", "")
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # 🔥 FIX: Stop engine if it's already running loops from previous turns
        if engine._inLoop:
            engine.endLoop()
        
        voices = engine.getProperty('voices')
        voice_id = None
        
        if gender == "Female":
            for v in voices:
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    voice_id = v.id
                    break
        else: 
            for v in voices:
                if "david" in v.name.lower() or "male" in v.name.lower():
                    voice_id = v.id
                    break
        
        if voice_id is None and voices: voice_id = voices[0].id
        
        engine.setProperty('voice', voice_id)
        engine.setProperty('rate', 160)
        
        # Unique filename with timestamp to prevent cache/lock issues
        filename = f"gd_{gender}_{int(time.time())}_{uuid.uuid4().hex[:4]}.mp3"
        
        engine.save_to_file(clean_text, filename)
        engine.runAndWait()
        
        # Wait a bit to ensure file write matches system speed
        time.sleep(0.5) 
        
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return None