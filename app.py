import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import PyPDF2
import speech_recognition as sr
import os
import base64

# Import Modules
import interview_bot
import posture_check
import db_connect
import gd_bot
import test_bot

# ---------------------------------------------------------
# HELPER FUNCTION: AUTO-PLAY AUDIO (INVISIBLE)
# ---------------------------------------------------------
def autoplay_audio(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        print(f"Autoplay Error: {e}")

# ---------------------------------------------------------
# 1. UI CONFIGURATION (MODERN ORGANIC WOOD THEME - FAWN EDITION)
# ---------------------------------------------------------
st.set_page_config(page_title="Sakshat-Kaar AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    /* --- THEME: MODERN ORGANIC WOOD (FAWN EDITION) --- */
    
    /* 1. Global App Background & Text */
    .stApp {
        background-color: #FAF3E0; /* Oat/Almond Background */
        color: #3E2723; /* Dark Mocha Text */
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 2. Headers */
    h1, h2, h3 {
        color: #4E342E !important; /* Dark Truffle */
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* 3. Sidebar (UPDATED: Fawn Background & Darker Text) */
    section[data-testid="stSidebar"] {
        background-color: #EBC7A8; /* Warm Fawn Color */
        border-right: 2px solid #8D6E63; /* Wood Border */
    }
    
    /* Sidebar Text & Labels (Darker Shade for Contrast) */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #2b1b17 !important; /* Deep Espresso (Almost Black-Brown) */
        font-weight: 700; 
    }

    /* 4. Input Fields (Creamy & Clean) */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stTextArea > div > div > textarea {
        background-color: #FFFDF5; /* Very Light Cream */
        color: #3E2723;
        border: 2px solid #8D6E63; /* Soft Brown Border */
        border-radius: 8px; 
        box-shadow: 0 2px 0px rgba(62, 39, 35, 0.2); 
    }
    
    /* 5. Buttons (Caramel/Terracotta Accent) */
    .stButton > button {
        background-color: #C17A46; /* Terracotta/Caramel */
        color: #FFFFFF;
        border: 2px solid #5D4037;
        border-radius: 8px;
        box-shadow: 0 4px 0px #5D4037; /* Hard Wood Shadow */
        font-weight: 700;
        text-transform: uppercase;
        transition: all 0.1s ease;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background-color: #A0522D; /* Darker Sienna */
        color: #FFFFFF;
        transform: translateY(2px);
        box-shadow: 0 2px 0px #5D4037;
    }

    /* 6. Custom Chat Bubbles (Earthy Tones) */
    .piyush-box, .anjali-box, .user-box, .report-card {
        padding: 18px;
        border-radius: 12px;
        box-shadow: 4px 4px 0px #A1887F; /* Hard Shadow */
        margin-bottom: 20px;
        color: #3E2723;
        font-size: 16px;
        line-height: 1.5;
        border: 2px solid #8D6E63;
    }

    .piyush-box { 
        background-color: #FFE4C4; /* Bisque */
        border-left: 8px solid #D2691E; 
    }
    
    .anjali-box { 
        background-color: #E8F5E9; /* Soft Sage */
        border-left: 8px solid #558B2F; 
    }
    
    .user-box { 
        background-color: #FFFFFF; 
        text-align: right; 
        border-right: 8px solid #8D6E63; 
    }
    
    .report-card {
        background-color: #FFF8E1; 
        border: 2px solid #D7CCC8;
    }

    /* 7. Alerts */
    .stAlert {
        background-color: #FFF3E0;
        color: #3E2723;
        border: 2px solid #FFCC80;
        border-radius: 8px;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #8D6E63;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATES
# ---------------------------------------------------------
if 'gd_active' not in st.session_state: st.session_state['gd_active'] = False
if 'gd_ended' not in st.session_state: st.session_state['gd_ended'] = False
if 'gd_messages' not in st.session_state: st.session_state['gd_messages'] = []
if 'gd_report' not in st.session_state: st.session_state['gd_report'] = ""
if 'gd_topic' not in st.session_state: st.session_state['gd_topic'] = "Loading..."
if 'last_hr_feedback' not in st.session_state: st.session_state['last_hr_feedback'] = ""
if 'gd_start_time' not in st.session_state: st.session_state['gd_start_time'] = None
if 'gd_duration' not in st.session_state: st.session_state['gd_duration'] = 10
if 'user_word_count' not in st.session_state: st.session_state['user_word_count'] = 0

if 'question' not in st.session_state: st.session_state['question'] = None
if 'resume_text' not in st.session_state: st.session_state['resume_text'] = ""
if 'answer_input' not in st.session_state: st.session_state['answer_input'] = ""

if 'test_stage' not in st.session_state: st.session_state['test_stage'] = 'setup'
if 'r1_questions' not in st.session_state: st.session_state['r1_questions'] = []
if 'r1_answers' not in st.session_state: st.session_state['r1_answers'] = {}
if 'r1_score' not in st.session_state: st.session_state['r1_score'] = 0
if 'r2_questions' not in st.session_state: st.session_state['r2_questions'] = []
if 'r2_responses' not in st.session_state: st.session_state['r2_responses'] = {}
if 'r2_count' not in st.session_state: st.session_state['r2_count'] = 2

# ---------------------------------------------------------
# 3. AUDIO RECORDER (BALANCED FOR INTERVIEW & GD)
# ---------------------------------------------------------
def record_audio():
    r = sr.Recognizer()
    
    # 🔥 BALANCED SETTINGS (Works for both Quiet & Dynamic Environments)
    r.dynamic_energy_threshold = True # Let it adapt to background noise
    # r.energy_threshold = 400 # Removed fixed threshold to allow auto-adjustment
    
    try:
        with sr.Microphone() as source:
            # Adjustment time: 0.5s (Fast enough, but stable)
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            st.toast("🎤 Speak NOW!", icon="🎙️")
            
            try:
                # Timeout increased to 8s (More time to think in GD/Interview)
                audio = r.listen(source, timeout=8, phrase_time_limit=20)
                st.toast("Processing audio...", icon="⏳")
                
                # Using Indian English model for better accuracy
                text = r.recognize_google(audio, language="en-IN")
                return text
            except sr.WaitTimeoutError:
                st.toast("⚠️ No speech detected.", icon="❌")
                return None
            except sr.UnknownValueError:
                st.toast("⚠️ Could not understand audio.", icon="❌")
                return None
                
    except Exception as e:
        print(f"Mic Error: {e}") 
        return None

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Sakshat-Kaar AI")
    
    # NAVIGATION
    page = st.radio("Navigate", ["🎥 Interview", "🗣️ GD Simulator", "📈 Reports", "📝 Aptitude & Code Test"])
    
    st.divider()
    st.subheader("👤 Profile")
    
    username = st.text_input("Candidate Name", "Aditya", key="sb_name")
    
    roles_list = [
        "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Data Scientist", "AI/ML Engineer", "DevOps Engineer", 
        "Product Manager", "Data Analyst", "Business Analyst",
        "QA / Test Engineer", "Cyber Security Analyst", "Android/iOS Developer"
    ]
    target_role = st.selectbox("Target Role", roles_list, key="sb_role")
    
    companies_list = [
        "Google", "Microsoft", "Amazon", "Meta", "Netflix", "Apple",
        "TCS", "Infosys", "Wipro", "Accenture", "Cognizant",
        "Uber", "Adobe", "Salesforce", "Tesla", "Oracle",
        "Goldman Sachs", "JPMorgan Chase", "Morgan Stanley",
        "Swiggy", "Zomato", "Flipkart", "Paytm",
        "Early Stage Startup", "Unicorn Startup"
    ]
    target_company = st.selectbox("Target Company", companies_list, key="sb_comp")
    
    # --- DYNAMIC DIFFICULTY SLIDER ---
    difficulty = st.select_slider(
        "Interview Difficulty", 
        options=["Fresher (Easy)", "Intermediate (Medium)", "Hard", "Expert"],
        value="Intermediate (Medium)", 
        key="sb_diff"
    )

    # 🔥 COLOR LOGIC BASED ON SELECTION
    slider_color = "#C17A46" # Default
    if "Easy" in difficulty: 
        slider_color = "#2E8B57" # Green
    elif "Medium" in difficulty: 
        slider_color = "#1E90FF" # Blue
    elif "Hard" in difficulty: 
        slider_color = "#DC143C" # Red
    elif "Expert" in difficulty: 
        slider_color = "#8B0000" # Dark Red

    st.markdown(f"""
    <style>
    div[data-testid="stSlider"] > div > div > div > div {{
        background-color: {slider_color} !important;
    }}
    div[data-testid="stSlider"] .st-bo {{
        background-color: {slider_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Resume", type="pdf", key="sb_resume")
    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            st.session_state['resume_text'] = "".join([page.extract_text() for page in reader.pages])
            st.success("Resume Active")
        except: st.error("Error")
    
    if db_connect.sessions_collection is not None:
        st.caption("🟢 DB Connected")

# ---------------------------------------------------------
# 5. PAGE LOGIC
# ---------------------------------------------------------

# === PAGE 1: INTERVIEW ===
if page == "🎥 Interview":
    st.title("🎥 1-on-1 Technical Interview")
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader("The Challenge")
        topic = st.text_input("Enter Topic (e.g., DSA, System Design)", "DSA", key="t1_topic")
        
        if st.button("Generate Question 🎲", key="t1_gen"):
            with st.spinner("Generating..."):
                q = interview_bot.generate_interview_question(target_role, topic, difficulty, st.session_state['resume_text'], target_company)
                st.session_state['question'] = q
        
        if st.session_state['question']:
            st.info(f"Q: {st.session_state['question']}")
            
            c_mic, c_txt = st.columns([1, 4])
            with c_mic:
                if st.button("🎙️ Record", key="t1_rec"):
                    txt = record_audio()
                    if txt: 
                        st.session_state['answer_input'] = txt
                        st.rerun()
            
            ans = st.text_area("Your Answer", value=st.session_state['answer_input'], key="t1_ans")
            
            if st.button("Submit & Analyze", key="t1_sub"):
                fb = interview_bot.analyze_answer(st.session_state['question'], ans)
                st.markdown(fb)
                if db_connect.sessions_collection is not None:
                    db_connect.sessions_collection.insert_one({
                        "user": username, 
                        "type": "Interview", 
                        "q": st.session_state['question'], 
                        "a": ans, 
                        "fb": str(fb), 
                        "time": datetime.now()
                    })

    with c2:
        st.subheader("Posture Coach")
        if st.toggle("Camera On", key="t1_cam"):
            analyzer = posture_check.PostureAnalyzer()
            cap = cv2.VideoCapture(0)
            ph = st.empty()
            while True:
                ret, frame = cap.read()
                if not ret: break
                frame, status = analyzer.process_frame(frame)
                ph.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=status)
                time.sleep(0.05)

# === PAGE 2: GD SIMULATOR ===
elif page == "🗣️ GD Simulator":
    st.title("🗣️ AI Group Discussion Simulator")
    
    if not st.session_state['gd_active'] and not st.session_state['gd_ended']:
        st.info("👋 Welcome! Piyush (Assertive) & Anjali (Calm) are waiting.")
        dur_mins = st.selectbox("Select Duration (Min)", [5, 10, 15], key="gd_dur")
        
        if st.button("🚀 Enter GD Room", key="start_gd"):
            st.session_state['gd_active'] = True
            st.session_state['gd_duration'] = dur_mins
            st.session_state['gd_start_time'] = datetime.now()
            st.session_state['gd_messages'] = []
            st.session_state['gd_report'] = ""
            
            with st.spinner("Moderator is setting the topic..."):
                topic = gd_bot.generate_gd_topic()
                st.session_state['gd_topic'] = topic
                st.session_state['gd_messages'].append({"role": "Moderator", "text": f"Topic: {topic}. Piyush, please start."})
            
            st.success(f"📢 Topic: {topic}")
            st.toast("⏳ 5 Seconds to read the topic...", icon="⏳")
            time.sleep(5)
            
            with st.spinner("Piyush is starting..."):
                p_txt = gd_bot.get_piyush_response(topic, "Start")
                p_audio = gd_bot.text_to_speech(p_txt, "Male")
                st.session_state['gd_messages'].append({"role": "Piyush", "text": p_txt})
                autoplay_audio(p_audio)
                word_count = len(p_txt.split())
                wait_time = (word_count / 130) * 60 + 1
                time.sleep(wait_time)
                
            st.rerun()

    elif st.session_state['gd_ended']:
        st.success(f"🏁 Session Ended: {st.session_state['gd_topic']}")
        if st.session_state['gd_report']:
            st.markdown(f'<div class="report-card">{st.session_state["gd_report"]}</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Generating Performance Report..."):
                hist = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state['gd_messages']])
                report = gd_bot.generate_final_report(st.session_state['gd_topic'], hist)
                st.session_state['gd_report'] = report
                if db_connect.sessions_collection is not None:
                    db_connect.sessions_collection.insert_one({
                        "user": username,
                        "type": "Group Discussion",
                        "topic": st.session_state['gd_topic'],
                        "report": report,
                        "time": datetime.now()
                    })
                st.rerun()
        
        if st.button("🔄 Start New Session"):
            st.session_state['gd_active'] = False
            st.session_state['gd_ended'] = False
            st.rerun()

    else:
        elapsed = datetime.now() - st.session_state['gd_start_time']
        rem = (st.session_state['gd_duration'] * 60) - elapsed.total_seconds()
        
        if rem <= 0:
            st.session_state['gd_active'] = False
            st.session_state['gd_ended'] = True
            st.rerun()
        
        c_top, c_btn = st.columns([4, 1])
        with c_top: st.info(f"📢 Topic: {st.session_state['gd_topic']}")
        with c_btn: 
            if st.button("🔴 Stop", key="stop_gd"):
                st.session_state['gd_active'] = False
                st.session_state['gd_ended'] = True
                st.rerun()
        
        st.progress(max(0.0, min(1.0, rem/(st.session_state['gd_duration']*60))))
        st.caption(f"Time Remaining: {int(rem//60)}m {int(rem%60)}s")
        
        col_chat, col_stats = st.columns([2, 1])
        with col_chat:
            with st.container(height=450):
                for msg in st.session_state['gd_messages']:
                    if msg['role'] == "Piyush": 
                        st.markdown(f'<div class="piyush-box">🔴 <b>Piyush:</b> {msg["text"]}</div>', unsafe_allow_html=True)
                    elif msg['role'] == "Anjali": 
                        st.markdown(f'<div class="anjali-box">🔵 <b>Anjali:</b> {msg["text"]}</div>', unsafe_allow_html=True)
                    elif msg['role'] == "You": 
                        st.markdown(f'<div class="user-box">🟢 <b>You:</b> {msg["text"]}</div>', unsafe_allow_html=True)
                    elif msg['role'] == "Moderator":
                        st.write(f"**Mod:** {msg['text']}")
            
            st.write("---")
            if st.button("🎙️ Jump In (Record)", key="jump_in"):
                user_text = record_audio()
                if user_text:
                    st.session_state['gd_messages'].append({"role": "You", "text": user_text})
                    st.session_state['user_word_count'] += len(user_text.split())
                    hist = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state['gd_messages']])
                    
                    st.markdown(f'<div class="user-box">🟢 <b>You:</b> {user_text}</div>', unsafe_allow_html=True)
                    fb = gd_bot.analyze_turn(st.session_state['gd_topic'], user_text, hist)
                    st.session_state['last_hr_feedback'] = fb
                    
                    with st.spinner("Anjali is responding..."):
                        a_txt = gd_bot.get_anjali_response(st.session_state['gd_topic'], hist)
                        a_audio = gd_bot.text_to_speech(a_txt, "Female")
                        st.session_state['gd_messages'].append({"role": "Anjali", "text": a_txt})
                        st.markdown(f'<div class="anjali-box">🔵 <b>Anjali:</b> {a_txt}</div>', unsafe_allow_html=True)
                        autoplay_audio(a_audio)
                        time.sleep((len(a_txt.split()) / 130) * 60 + 2)
                    
                    with st.spinner("Piyush is responding..."):
                        hist_updated = hist + f"\nAnjali: {a_txt}"
                        p_txt = gd_bot.get_piyush_response(st.session_state['gd_topic'], hist_updated)
                        p_audio = gd_bot.text_to_speech(p_txt, "Male")
                        st.session_state['gd_messages'].append({"role": "Piyush", "text": p_txt})
                        st.markdown(f'<div class="piyush-box">🔴 <b>Piyush:</b> {p_txt}</div>', unsafe_allow_html=True)
                        autoplay_audio(p_audio)
                        time.sleep((len(p_txt.split()) / 130) * 60 + 2)

                    st.rerun()
                else:
                    st.warning("Could not hear you. Please try again.")

        with col_stats:
            st.metric("Your Words", st.session_state['user_word_count'])
            if st.session_state['last_hr_feedback']:
                st.info(f"💡 HR Tip: {st.session_state['last_hr_feedback']}")

# === PAGE 3: REPORTS ===
elif page == "📈 Reports":
    st.title("📈 Performance Reports")
    
    if st.button("🔄 Refresh Data"):
        if db_connect.sessions_collection is not None:
            data = list(db_connect.sessions_collection.find({"user": username}).sort("time", -1))
            
            if not data:
                st.warning("No records found for this user.")
            else:
                for d in data:
                    date_obj = d.get('time')
                    date_str = date_obj.strftime("%d %b %Y, %I:%M %p") if date_obj else "Unknown Date"
                    session_type = d.get('type', 'Unknown')

                    with st.expander(f"📅 {date_str}  |  {session_type}"):
                        if session_type == "Interview":
                            st.markdown(f"**🧐 Question:** {d.get('q')}")
                            st.info(f"**🗣️ Your Answer:** {d.get('a')}")
                            st.markdown("---")
                            st.markdown(f"**🛡️ AI Feedback:**\n{d.get('fb')}")
                        elif session_type == "Group Discussion":
                            st.markdown(f"**📢 Topic:** {d.get('topic')}")
                            st.markdown("---")
                            st.markdown(d.get('report'))
                        elif session_type == "Placement Test":
                            st.markdown(f"**🔢 Round 1 Score:** {d.get('r1_score')}")
                            st.markdown("---")
                            st.markdown("**🛡️ Final Analysis:**")
                            st.markdown(d.get('final_feedback'))
        else:
            st.error("Database not connected")

# === PAGE 4: PLACEMENT TEST ===
elif page == "📝 Aptitude & Code Test":
    st.title("📝 Full Stack Placement Test")
    
    if st.session_state['test_stage'] == 'setup':
        st.subheader("⚙️ Configure Your Test")
        c1, c2 = st.columns(2)
        with c1:
            r1_count = st.selectbox("Round 1 (Aptitude) Questions", [5, 10, 20, 40])
        with c2:
            st.session_state['r2_count'] = st.selectbox("Round 2 (Coding) Questions", [1, 2, 5], index=1)
            
        if st.button("🚀 Start Placement Test"):
            with st.spinner("Generating Aptitude Paper (Round 1)..."):
                qs = test_bot.generate_aptitude_questions(target_role, target_company, r1_count)
                if qs:
                    st.session_state['r1_questions'] = qs
                    st.session_state['r1_answers'] = {i: None for i in range(len(qs))}
                    st.session_state['test_stage'] = 'r1_active'
                    st.rerun()
                else:
                    st.error("AI could not generate questions. Try again.")

    elif st.session_state['test_stage'] == 'r1_active':
        st.subheader("🧠 Round 1: Logical & Aptitude")
        st.info("Select the correct option for each question.")
        
        with st.form("r1_form"):
            for idx, q_data in enumerate(st.session_state['r1_questions']):
                st.markdown(f"**Q{idx+1}. {q_data['q']}**")
                st.session_state['r1_answers'][idx] = st.radio(
                    f"Select Option for Q{idx+1}", 
                    q_data['options'], 
                    key=f"r1_q_{idx}", 
                    index=None
                )
                st.divider()
            
            submit_r1 = st.form_submit_button("✅ Submit Round 1")
            
            if submit_r1:
                score = 0
                total = len(st.session_state['r1_questions'])
                for idx, q in enumerate(st.session_state['r1_questions']):
                    user_choice = st.session_state['r1_answers'].get(idx)
                    if user_choice:
                        try:
                            u_idx = q['options'].index(user_choice)
                            if u_idx == q.get('correct_index'):
                                score += 1
                        except ValueError:
                            pass
                st.session_state['r1_score'] = score
                st.session_state['test_stage'] = 'r1_result'
                st.rerun()

    elif st.session_state['test_stage'] == 'r1_result':
        score = st.session_state['r1_score']
        total = len(st.session_state['r1_questions'])
        percentage = (score / total) * 100 if total > 0 else 0
        
        st.subheader("📊 Round 1 Result")
        col1, col2 = st.columns(2)
        col1.metric("Score", f"{score}/{total}")
        col2.metric("Percentage", f"{percentage:.1f}%")
        
        with st.expander("🔍 View Correct Answers"):
            for idx, q in enumerate(st.session_state['r1_questions']):
                correct_opt = q['options'][q['correct_index']]
                user_opt = st.session_state['r1_answers'].get(idx, "Not Answered")
                status = "✅" if user_opt == correct_opt else "❌"
                st.write(f"**Q{idx+1}:** {status} You: *{user_opt}* | Correct: **{correct_opt}**")

        if percentage >= 50:
            st.success("🎉 Congratulations! You have cleared Round 1.")
            st.balloons()
            st.markdown("### Prepare for Round 2: Coding Assessment")
            if st.button("⚔️ Start Round 2 (Coding)"):
                with st.spinner("Generating Coding Problems..."):
                    count = st.session_state.get('r2_count', 2) 
                    qs = test_bot.generate_coding_questions(target_role, target_company, count)
                    if qs:
                        st.session_state['r2_questions'] = qs
                        st.session_state['test_stage'] = 'r2_active'
                        st.rerun()
                    else:
                        st.error("Failed to load Round 2.")
        else:
            st.error("❌ You did not clear the cutoff (50%). Better luck next time!")
            if st.button("🔄 Restart Test"):
                st.session_state['test_stage'] = 'setup'
                st.rerun()

    elif st.session_state['test_stage'] == 'r2_active':
        st.subheader("💻 Round 2: Technical Coding")
        tabs = st.tabs([f"Problem {i+1}" for i in range(len(st.session_state['r2_questions']))])
        
        for i, tab in enumerate(tabs):
            q = st.session_state['r2_questions'][i]
            with tab:
                st.markdown(f"### {q['title']}")
                st.write(q['desc'])
                st.info(f"**Example Input:** `{q['example_in']}`\n\n**Example Output:** `{q['example_out']}`")
                code = st.text_area(f"Write your Python code for Problem {i+1}", height=200, key=f"code_{i}")
                
                if st.button(f"Submit Code {i+1}", key=f"sub_code_{i}"):
                    if code:
                        with st.spinner("Compiling & Evaluating..."):
                            eval_res = test_bot.evaluate_code_submission(q['desc'], code)
                            st.session_state['r2_responses'][i] = eval_res
                            st.success(f"Evaluated! Score: {eval_res['score']}/10")
                            st.json(eval_res)
                    else:
                        st.warning("Please write some code first.")
        
        st.divider()
        if st.button("🏁 Finish Test & Get Report"):
             st.session_state['test_stage'] = 'final_result'
             st.rerun()

    elif st.session_state['test_stage'] == 'final_result':
        st.title("📑 Final Placement Report")
        r1_s = st.session_state['r1_score']
        r1_t = len(st.session_state['r1_questions'])
        r2_feedbacks = [v['feedback'] for k,v in st.session_state['r2_responses'].items()]
        
        with st.spinner("Generating Detailed Analysis..."):
            final_feedback = test_bot.generate_test_analysis(r1_s, r1_t, r2_feedbacks)
            st.markdown(final_feedback)
            if db_connect.sessions_collection is not None:
                db_connect.sessions_collection.insert_one({
                    "user": username,
                    "type": "Placement Test",
                    "r1_score": r1_s,
                    "r2_eval": st.session_state['r2_responses'],
                    "final_feedback": final_feedback,
                    "time": datetime.now()
                })
                st.toast("Result saved to Database!")
        
        if st.button("🏠 Back to Home"):
            st.session_state['test_stage'] = 'setup'
            st.rerun()