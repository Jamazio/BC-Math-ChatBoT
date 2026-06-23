import os
import json
import streamlit as pd
import streamlit as st
from datetime import datetime
from groq import Groq

# =====================================================================
# 1. EXACT ONEDRIVE ABSOLUTE PATH CONFIGURATION (OPTION B)
# =====================================================================
ONEDRIVE_DIR = r"C:\Users\Jamazio Mcphee\OneDrive - Benedict College\School\SURI RESEARCH\Chatbot_Data"
LOG_FILE_PATH = os.path.join(ONEDRIVE_DIR, "communication_logs.txt")
SURVEY_FILE_PATH = os.path.join(ONEDRIVE_DIR, "survey_feedback.json")

# Ensure the OneDrive directory exists immediately on startup
if not os.path.exists(ONEDRIVE_DIR):
    os.makedirs(ONEDRIVE_DIR)

# =====================================================================
# 2. LOCAL PROJECT FILE LOADERS
# =====================================================================
def load_campus_context():
    """Loads Benedict College context data if available."""
    if os.path.exists("benedict_info.txt"):
        with open("benedict_info.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Campus context unavailable."

def load_survey_questions():
    """Loads strategic survey questions from the local JSON file."""
    if os.path.exists("survey_questions.json"):
        with open("survey_questions.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {"questions": [{"id": "q1", "text": "How helpful was the tutor?", "type": "scale"}]}

# =====================================================================
# 3. ONEDRIVE DATA LOGGING FUNCTIONS
# =====================================================================
def save_chat_log_to_onedrive(user_query, ai_response):
    """Appends conversational interaction logs directly to OneDrive."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\nUSER: {user_query}\nTIGERMATH AI: {ai_response}\n{'='*50}\n"
    
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

def save_survey_to_onedrive(survey_responses):
    """Appends strategic user feedback survey loops to OneDrive JSON."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "timestamp": timestamp,
        "responses": survey_responses
    }
    
    data = []
    if os.path.exists(SURVEY_FILE_PATH):
        with open(SURVEY_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
                
    data.append(payload)
    
    with open(SURVEY_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =====================================================================
# 4. INITIALIZE STREAMLIT APP & GROQ CLIENT
# =====================================================================
st.set_page_config(page_title="BC TigerMath AI", page_icon="🐯", layout="wide")
st.title("🐯 BC TigerMath AI Chatbot")
st.subheader("SURI Research Portal - Socratic Mathematics Tutor")

# Fetch API Key securely from local Streamlit secrets (ignored by Git)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Groq API Key missing! Ensure it is set up in your local secrets.toml file.")
    st.stop()

# Initialize conversational state histories
if "messages" not in st.session_state:
    st.session_state.messages = []
if "survey_submitted" not in st.session_state:
    st.session_state.survey_submitted = False

# Load campus data & structure system prompt
campus_info = load_campus_context()
SYSTEM_PROMPT = f"""
You are BC TigerMath AI, an advanced, interactive Socratic mathematics tutor for students at Benedict College.
Your purpose is to guide students from Algebra through Calculus by asking guiding questions, offering hints,
and walking them through mathematical frameworks step-by-step. Do not simply give the answer away immediately.
Context about Benedict College: {campus_info}
"""

# =====================================================================
# 5. SIDEBAR: CALCULATOR & SYSTEM MONITOR
# =====================================================================
with st.sidebar:
    st.header("🧮 Math Tools & Controls")
    st.markdown("---")
    st.info(f"💾 **Data Target:**\n`{ONEDRIVE_DIR}`")
    
    # Advanced Calculator Panel Mockup
    st.markdown("### Quick Equation Analyzer")
    calc_expr = st.text_input("Enter expression (e.g., f(x) = x^2 + 3x):")
    if calc_expr:
        st.success(f"Expression locked! Ask the chatbot to help you differentiate or integrate it.")

# =====================================================================
# 6. MAIN CHAT INTERFACE
# =====================================================================
# Render historical messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capture native user chat inputs
if user_input := st.chat_input("Ask a math question or request a strategic hint..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Compile messages sequence for Groq Inference
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]
    
    # Trigger AI completion model
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=api_messages,
            temperature=0.4,
            max_tokens=1024,
            stream=False
        )
        ai_response = completion.choices[0].message.content
        response_placeholder.markdown(ai_response)
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # AUTOMATED LOGGING: Save interaction straight to OneDrive path
    save_chat_log_to_onedrive(user_input, ai_response)

# =====================================================================
# 7. STRATEGIC USER FEEDBACK LOOP (SURVEY SYSTEM)
# =====================================================================
if len(st.session_state.messages) >= 4 and not st.session_state.survey_submitted:
    st.markdown("---")
    st.markdown("### 📊 SURI Research Project Evaluation")
    st.write("Please provide quick strategic feedback regarding your Socratic tutoring interaction:")
    
    questions_data = load_survey_questions()
    responses = {}
    
    with st.form("research_feedback_form"):
        for q in questions_data.get("questions", []):
            if q["type"] == "scale":
                responses[q["id"]] = st.slider(q["text"], 1, 5, 3)
            elif q["type"] == "text":
                responses[q["id"]] = st.text_area(q["text"])
                
        submitted = st.form_submit_form_button("Submit Strategic Evaluation")
        if submitted:
            # CLOUD STORAGE PIPELINE: Stream metrics directly to OneDrive
            save_survey_to_onedrive(responses)
            st.session_state.survey_submitted = True
            st.success("Feedback successfully pushed to your OneDrive directory!")
            st.rerun()
