import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from supabase import create_client, Client
import time
import json
import os
from datetime import datetime

# =====================================
# 1. CORE DATA FUNCTIONS
# =====================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def load_survey_questions(filepath='survey_questions.json'):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_feedback(student_id, question_id, response):
    try:
        data = {
            "student_id": student_id,
            "question_id": str(question_id),
            "response": str(response)
        }
        supabase.table("student_feedback").insert(data).execute()
    except Exception as e:
        st.error(f"Failed to save feedback to Supabase: {e}")

def log_communication(user_input, bot_response):
    onedrive_dir = r"C:\Users\Jamazio Mcphee\OneDrive - Benedict College"
    if not os.path.exists(onedrive_dir):
        os.makedirs(onedrive_dir, exist_ok=True)
        
    log_file_path = os.path.join(onedrive_dir, "math_bot_chat_logs.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\nUser: {user_input}\nBot: {bot_response}\n---\n"
    
    try:
        with open(log_file_path, 'a', encoding="utf-8") as file:
            file.write(log_entry)
    except Exception as e:
        pass

# =====================================
# 2. PAGE SETUP & CONFIG
# =====================================
st.set_page_config(page_title="BC TigerMath AI", page_icon="🐅", layout="wide")

st.markdown("""
    <style>
    h1 { color: #FFD700 !important; font-family: 'Arial Black', Gadget, sans-serif; }
    .stCaption { color: #F0F2F6 !important; font-style: italic; }
    div[data-testid="stSidebar"] { background-color: #1A1A1A; }
    div[data-testid="stChatInput"] { border: 2px solid #4C145E !important; border-radius: 12px; }
    div[data-testid="stPopover"] > button {
        background-color: #262730 !important;
        color: #FFD700 !important;
        border: 1px solid #4C145E !important;
        border-radius: 8px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================
# 3. INITIALIZE SESSION STATE VARIABLES
# =====================================
if "language" not in st.session_state:
    st.session_state.language = "English"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "custom_style" not in st.session_state:
    st.session_state.custom_style = ""
if "target_symbol" not in st.session_state:
    st.session_state.target_symbol = None
if "session_ended" not in st.session_state:
    st.session_state.session_ended = False

def send_symbol_to_state(symbol):
    st.session_state.target_symbol = symbol

# =====================================
# 4. SIDEBAR CONFIGURATION (FEEDBACK REMOVED)
# =====================================
with st.sidebar:
    st.header("📖 Training Guides")
    if st.button("🎓 Student Guide Walkthrough", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Start Student Guide."})
        st.rerun()
        
    if st.button("👩‍🏫 Faculty Guide Walkthrough", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Start Faculty Guide."})
        st.rerun()

    st.write("---")
    with st.expander("🌍 Language & Style Settings", expanded=False):
        st.radio("Choose Language", ["English", "Español"], key="language")
        st.text_input("🎭 Custom Persona / Style:", key="custom_style")

    st.write("---")
    st.header("Control Panel")
    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_ended = False
        st.rerun()

# =====================================
# 5. MAIN CONTENT AREA
# =====================================
st.title("🐅 BC TigerMath AI")
st.caption("Your Campus BC Math Specialist | Created by Mark Wells and Jamazio Mcphee")
st.write("---")

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================
# 6. INLINE CHAT FEEDBACK FORM
# =====================================
# Only show this option if there is an active conversation
if len(st.session_state.messages) > 1:
    
    # Show the End Session button if they haven't clicked it yet
    if not st.session_state.session_ended:
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏁 End Conversation & Leave Feedback", use_container_width=True):
                st.session_state.session_ended = True
                st.rerun()

    # If the session is ended, present the survey as an AI chat message
    if st.session_state.session_ended:
        with st.chat_message("assistant"):
            st.markdown("### 📝 Session Wrap-Up")
            st.markdown("Thank you for chatting! Please let me know how I did before you go.")
            
            questions = load_survey_questions()
            if questions:
                with st.form("inline_feedback_form"):
                    responses = {}
                    for i, q in enumerate(questions):
                        if isinstance(q, str):
                            responses[f"q{i+1}"] = st.slider(q, 1, 5) if "scale" in q.lower() or "confident" in q.lower() else st.text_area(q)
                        else:
                            q_text = q.get("question", "Feedback Question")
                            q_id = q.get("id", f"q{i+1}")
                            responses[q_id] = st.slider(q_text, 1, 5) if q.get("type") == "scale" else st.text_area(q_text)
                                
                    submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
                    if submitted:
                        for q_id, resp in responses.items():
                            save_feedback(student_id="Student_01", question_id=q_id, response=resp)
                        st.success("Feedback securely sent to Supabase! Have a great day! 🐅")
            else:
                st.info("Survey questions not found.")

# =====================================
# 7. MATH TOOLS & CHAT INPUT
# =====================================
# Hide the input box if the session is ended to force completion
if not st.session_state.session_ended:
    
    if st.session_state.target_symbol:
        safe_symbol = st.session_state.target_symbol.replace("'", "\\'")
        js_injector = f"""
        <script>
        var textarea = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (textarea) {{
            var valueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            valueSetter.call(textarea, textarea.value + '{safe_symbol}');
            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            textarea.focus();
        }}
        </script>
        """
        components.html(js_injector, height=0, width=0)
        st.session_state.target_symbol = None  

    with st.popover("📐 Insert Math Symbols & Operations"):
        s_row1 = st.columns(6)
        s_row1[0].button("π", on_click=send_symbol_to_state, args=("π",))
        s_row1[1].button("√", on_click=send_symbol_to_state, args=("√(",))
        s_row1[2].button("²", on_click=send_symbol_to_state, args=("²",))
        s_row1[3].button("°", on_click=send_symbol_to_state, args=("°",))
        s_row1[4].button("θ", on_click=send_symbol_to_state, args=("θ",))
        s_row1[5].button("∞", on_click=send_symbol_to_state, args=("∞",))

    user_query = st.chat_input("Hi there! What math problem can I help you with today? 🐅")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Basic context payload
                messages_payload = [{"role": "system", "content": "You are a helpful math tutor. Keep responses brief."}]
                for msg in st.session_state.messages:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                response_stream = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages_payload,
                    stream=True
                )

                for chunk in response_stream:
                    content = getattr(chunk.choices[0].delta, "content", None)
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.003)
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                log_communication(user_query, full_response)

            except Exception as e:
                st.error("API Error. Please check your configuration.")
