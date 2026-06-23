import os
import json
import random
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import math
import re
# --- Added for Google Sheets Cloud Integration ---
import gspread
from google.oauth2.service_account import Credentials
# -------------------------------------------------

# =====================================
# 1. PAGE SETUP & CONFIG
# =====================================
st.set_page_config(
    page_title="BC TigerMath AI",
    page_icon="🐅",
    layout="wide"
)

# --- 📁 OneDrive & Data Logging Setup ---
LOCAL_ONEDRIVE_PATH = r"C:\Users\Jamazio Mcphee\OneDrive - Benedict College\School\SURI RESEARCH\Chatbot_Data"

# Smart Switch: Use your absolute OneDrive path on Windows, fall back to local directory on Cloud Linux
if os.path.exists(r"C:\Users"):
    ONEDRIVE_DIR = LOCAL_ONEDRIVE_PATH
else:
    ONEDRIVE_DIR = "Chatbot_Data"

LOG_FILE_PATH = os.path.join(ONEDRIVE_DIR, "communication_logs.txt")
FEEDBACK_FILE_PATH = os.path.join(ONEDRIVE_DIR, "survey_feedback.json")
SURVEY_QUESTIONS_FILE = "survey_questions.json"

# Create the folder automatically if it doesn't exist locally
os.makedirs(ONEDRIVE_DIR, exist_ok=True)

def load_survey_questions():
    """Reads survey questions from the local JSON file."""
    try:
        with open(SURVEY_QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return ["How confident do you feel about the math covered today?"]

def log_conversation(chat_history):
    """Appends the active session logs to OneDrive and streams context to Google Sheets."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏳ [CLOUD LOG] Starting full conversation sync to Google Sheets...")
    
    # 1. Local/OneDrive backup logging
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n--- TigerMath Session: {timestamp} ---\n")
            for msg in chat_history:
                f.write(f"{msg['role']}: {msg['content']}\n")
    except Exception as e:
        print(f"⚠️ Local OneDrive backup log skipped or failed: {e}")

    # 2. Live Cloud Google Sheet sync
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        secret_creds = dict(st.secrets["gcp_service_account"])
        secret_creds["private_key"] = secret_creds["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(secret_creds, scopes=scopes)
        gspread_client = gspread.authorize(creds)
        workbook = gspread_client.open("BC_TigerMath_Feedback_Logs")
        
        # Safe check for optional conversation tab, otherwise logs to main sheet1 row
        try:
            chat_sheet = workbook.worksheet("Chat_Logs")
            print("📁 Target Worksheet found: 'Chat_Logs'")
        except Exception:
            chat_sheet = workbook.sheet1
            print("📁 'Chat_Logs' tab not found, falling back to primary sheet tab index.")
            
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        style_used = st.session_state.get("custom_style", "Default Socratic")
        
        chat_sheet.append_row([timestamp, "Full Conversation Log History", history_str, style_used])
        print("✅ [CLOUD LOG] Full conversation log successfully added to Google Sheets!")
    except Exception as e:
        print(f"🔴 [GOOGLE SHEETS CHAT LOG ERROR]: {e}")
        st.sidebar.error(f"Chat Log Cloud Sync issue: {e}")

def save_survey_feedback(question, response):
    """Saves structured student feedback data to OneDrive and streams it directly to Google Sheets."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏳ [CLOUD LOG] Sending student feedback response to Google Sheets...")
    
    feedback_data = {
        "timestamp": timestamp,
        "question": question,
        "response": response
    }
    
    # 1. Local/OneDrive backup logging
    try:
        existing_data = []
        if os.path.exists(FEEDBACK_FILE_PATH):
            try:
                with open(FEEDBACK_FILE_PATH, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                pass
                
        existing_data.append(feedback_data)
        with open(FEEDBACK_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"⚠️ Local OneDrive feedback JSON backup skipped or failed: {e}")

    # 2. Live Cloud Google Sheet streaming
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        secret_creds = dict(st.secrets["gcp_service_account"])
        secret_creds["private_key"] = secret_creds["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(secret_creds, scopes=scopes)
        gspread_client = gspread.authorize(creds)
        
        sheet = gspread_client.open("BC_TigerMath_Feedback_Logs").sheet1
        style_used = st.session_state.get("custom_style", "Default Socratic")
        
        sheet.append_row([timestamp, question, response, style_used])
        print("✅ [CLOUD LOG] Student feedback row successfully added to Google Sheets!")
    except Exception as e:
        print(f"🔴 [GOOGLE SHEETS FEEDBACK ERROR]: {e}")
        st.sidebar.error(f"Spreadsheet Cloud Sync issue: {e}")


# --- 🎨 Custom CSS Injection: BC Purple & Tiger Gold Theme ---
st.markdown("""
<style>
h1 {
    color: #FFD700 !important;
    font-family: 'Arial Black', Gadget, sans-serif;
}
.stCaption {
    color: #F0F2F6 !important;
    font-style: italic;
}
div.stButton > button {
    background-color: #4C145E !important;
    color: #FFD700 !important;
    border: 2px solid #FFD700 !important;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    height: 40px;
    transition: all 0.3s ease;
    padding: 0px !important;
}
div.stButton > button:hover {
    background-color: #FFD700 !important;
    color: #4C145E !important;
    border: 2px solid #4C145E !important;
}
input:disabled {
    background-color: #262730 !important;
    color: #FFD700 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 18px !important;
    font-weight: bold !important;
    text-align: right !important;
    opacity: 1 !important;
}
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
# 2. MULTI-LANGUAGE UI DICTIONARY
# =====================================
UI_TEXT = {
    "English": {
        "caption": "Your Campus BC Math Specialist | Created by Mark Wells and Jamazio Mcphee",
        "lang_prompt": "🌍 Select Your Language",
        "calc_header": "🧮 Advanced Calculator",
        "calc_caption": "Compute math across all levels directly from your sidebar!",
        "ctrl_header": "Control Panel",
        "ctrl_info": "The BC Math Specialist is authenticated and ready to assist!",
        "reset_btn": "Reset Conversation",
        "quick_title": "**Quick-Load Problem Starters:**",
        "ql_1_btn": "➕ Algebra Setup",
        "ql_1_msg": "How do I solve a quadratic equation like x² - 5x + 6 = 0?",
        "ql_2_btn": "📐 Pre-Calc Help",
        "ql_2_msg": "Can you help me find the exact value of sin(π/3)?",
        "ql_3_btn": "📈 Calculus Rules",
        "ql_3_msg": "I need help finding the derivative of f(x) = x² * e^x.",
        "ql_4_btn": "📊 Stats & Data",
        "ql_4_msg": "How do I calculate the standard deviation or z-score of a dataset?",
        "chat_placeholder": "Hi there! What math problem can I help you with today? 🐅",
        "sys_prompt": "You MUST respond ONLY in English.",
        "error_msg": "Authentication or API Error. Please check your system configuration."
    },
    "Español": {
        "caption": "Tu Especialista Matemático BC | Creado por Mark Wells y Jamazio Mcphee",
        "lang_prompt": "🌍 Selecciona tu idioma",
        "calc_header": "🧮 Calculadora Avanzada",
        "calc_caption": "¡Realiza cálculos de todos los niveles desde la barra lateral!",
        "ctrl_header": "Panel de Control",
        "ctrl_info": "¡El Especialista Matemático BC está listo para ayudar!",
        "reset_btn": "Reiniciar Conversación",
        "quick_title": "**Iniciadores de Problemas Rápidos:**",
        "ql_1_btn": "➕ Álgebra",
        "ql_1_msg": "¿Cómo resuelvo una ecuación cuadrática como x² - 5x + 6 = 0?",
        "ql_2_btn": "📐 Pre-Cálculo",
        "ql_2_msg": "¿Puedes ayudarme a encontrar el valor exacto de sin(π/3)?",
        "ql_3_btn": "📈 Cálculo",
        "ql_3_msg": "Necesito ayuda para encontrar la derivada de f(x) = x² * e^x.",
        "ql_4_btn": "📊 Estadística",
        "ql_4_msg": "¿Cómo calculo la desviación estándar o el valor z de un conjunto de datos?",
        "chat_placeholder": "¡Hola! ¿Con qué problema de matemáticas te puedo ayudar hoy? 🐅",
        "sys_prompt": "Debes responder ÚNICAMENTE en español.",
        "error_msg": "Error de API o autenticación. Verifica la configuración de tu sistema."
    },
    "Français": {
        "caption": "Votre spécialiste mathématique BC | Créé por Mark Wells y Jamazio Mcphee",
        "lang_prompt": "🌍 Choisissez votre langue",
        "calc_header": "🧮 Calculatrice Avancée",
        "calc_caption": "Calculez des expressions de tous niveaux depuis la barra latérale !",
        "ctrl_header": "Panneau de Configuration",
        "ctrl_info": "Le spécialiste mathématique BC est prêt à vous aider !",
        "reset_btn": "Réinitialiser la Conversation",
        "quick_title": "**Démarreurs Rapides de Problèmes :**",
        "ql_1_btn": "➕ Algèbre",
        "ql_1_msg": "Comment résoudre une équation quadratique comme x² - 5x + 6 = 0 ?",
        "ql_2_btn": "📐 Pré-Calcul",
        "ql_2_msg": "Pouvez-vous m'aidez à trouver la valeur exacte de sin(π/3) ?",
        "ql_3_btn": "📈 Calcul",
        "ql_3_msg": "J'ai besoin d'aide pour trouver la dérivée de f(x) = x² * e^x.",
        "ql_4_btn": "📊 Statistiques",
        "ql_4_msg": "Comment calculer l'écart type ou le score z d'un ensemble de données ?",
        "chat_placeholder": "Bonjour ! Avec quel problème de mathématiques puis-je vous aider aujourd'hui ? 🐅",
        "sys_prompt": "Vous devez répondre UNIQUEMENT en français.",
        "error_msg": "Erreur d'authentification ou d'API. Veuillez vérifier votre configuration."
    },
    "Deutsch": {
        "caption": "Ihr BC Mathematik-Spezialist | Erstellt von Mark Wells und Jamazio Mcphee",
        "lang_prompt": "🌍 Sprache auswählen",
        "calc_header": "🧮 Erweiterter Rechner",
        "calc_caption": "Berechnen Sie mathematische Probleme aller Stufen in der Seitenleiste!",
        "ctrl_header": "Kontrollzentrum",
        "ctrl_info": "Der BC Mathematik-Spezialist ist authentifiziert und bereit zu helfen!",
        "reset_btn": "Konversation zurücksetzen",
        "quick_title": "**Schnellstart für Mathematikprobleme:**",
        "ql_1_btn": "➕ Algebra",
        "ql_1_msg": "Wie löse ich eine quadratische Gleichung wie x² - 5x + 6 = 0?",
        "ql_2_btn": "📐 Vorkalkül",
        "ql_2_msg": "Kannst du mir helfen, den exakten Wert von sin(π/3) zu finden?",
        "ql_3_btn": "📈 Analysis",
        "ql_3_msg": "Ich brauche Hilfe bei der Ableitung von f(x) = x² * e^x.",
        "ql_4_btn": "📊 Statistik",
        "ql_4_msg": "Wie bereche ich die Standardabweichung oder den Z-Wert eines Datensatzes?",
        "chat_placeholder": "Hallo! Bei welchem Mathematikproblem kann ich heute helfen? 🐅",
        "sys_prompt": "Du musst AUSSCHLIESSLICH auf Deutsch antworten.",
        "error_msg": "Authentifizierungs- oder API-Fehler. Bitte überprüfe deine Systemkonfiguration."
    }
}

# =====================================
# 3. INITIALIZE SESSION STATE VARIABLES
# =====================================
if "language" not in st.session_state:
    st.session_state.language = "English"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "calc_expression" not in st.session_state:
    st.session_state.calc_expression = ""
if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None
if "shown_resources" not in st.session_state:
    st.session_state.shown_resources = set()
if "custom_style" not in st.session_state:
    st.session_state.custom_style = ""
if "target_symbol" not in st.session_state:
    st.session_state.target_symbol = None

# --- Survey State Tracking Variables ---
if "survey_question" not in st.session_state:
    questions = load_survey_questions()
    st.session_state.survey_question = random.choice(questions)
if "survey_answered" not in st.session_state:
    st.session_state.survey_answered = False

# Load active language dictionary dynamically
lang = UI_TEXT.get(st.session_state.language, UI_TEXT["English"])

def send_symbol_to_state(symbol):
    st.session_state.target_symbol = symbol

# =====================================
# 4. SIDEBAR CONFIGURATION (CALCULATOR)
# =====================================
with st.sidebar:
    st.radio(
        "🌍 Choose Language",
        list(UI_TEXT.keys()),
        key="language"
    )

    st.text_input(
        "🎭 Custom Persona / Style:",
        placeholder="e.g., Southern style, surfer slang, hyper energetic...",
        key="custom_style"
    )

    st.write("---")
    st.header(lang["calc_header"])
    st.caption(lang["calc_caption"])

    def append_calc(char):
        if st.session_state.calc_expression in ["Error", "0"]:
            st.session_state.calc_expression = ""
        if char == "1/x":
            st.session_state.calc_expression += "1/("
        else:
            st.session_state.calc_expression += str(char)

    def clear_calc():
        st.session_state.calc_expression = ""

    def delete_last_calc():
        if st.session_state.calc_expression in ["Error", "0"]:
            st.session_state.calc_expression = ""
        else:
            st.session_state.calc_expression = st.session_state.calc_expression[:-1]

    def evaluate_calc():
        try:
            expr = st.session_state.calc_expression
            if not expr:
                return

            expr = expr.replace("×", "*").replace("÷", "/")
            expr = expr.replace("π", "pi").replace("e", "e")
            expr = expr.replace("√(", "sqrt(")

            expr = re.sub(r'(\d|pi|e)\s*([a-zA-Z\(])', r'\1*\2', expr)
            expr = re.sub(r'([\)])\s*([0-9a-zA-Z\(])', r'\1*\2', expr)
            expr = expr.replace("^", "**")
            open_brackets = expr.count("(")
            close_brackets = expr.count(")")
            if open_brackets > close_brackets:
                expr += ")" * (open_brackets - close_brackets)

            allowed_env = {
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "sqrt": math.sqrt,
                "ln": math.log,
                "log": math.log10,
                "pi": math.pi,
                "e": math.e,
                "__builtins__": None
            }
            raw_result = eval(expr, allowed_env, {})
            if isinstance(raw_result, (int, float)):
                rounded_result = round(raw_result, 10)
                if isinstance(rounded_result, float) and rounded_result.is_integer():
                    rounded_result = int(rounded_result)
                st.session_state.calc_expression = str(rounded_result)
        except Exception:
            st.session_state.calc_expression = "Error"

    st.text_input(
        label="Calculator Screen",
        value=st.session_state.calc_expression if st.session_state.calc_expression else "0",
        disabled=True,
        label_visibility="collapsed"
    )

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        st.button("CLR", key="btn_master_clr", on_click=clear_calc, use_container_width=True)
    with ctrl_col2:
        st.button("DEL", key="btn_master_del", on_click=delete_last_calc, use_container_width=True)
    with ctrl_col3:
        st.button("(", key="btn_master_lparen", on_click=append_calc, args=("(",), use_container_width=True)
    with ctrl_col4:
        st.button(")", key="btn_master_rparen", on_click=append_calc, args=(")",), use_container_width=True)

    calc_tabs = st.tabs(["🔢 Basic", "📐 Alg/Trig", "📈 Calc/Stat"])

    def render_calc_grid(buttons, unique_prefix):
        for r_idx, row in enumerate(buttons):
            cols = st.columns(len(row))
            for c_idx, char in enumerate(row):
                with cols[c_idx]:
                    if char == "=":
                        st.button(char, key=f"{unique_prefix}_{r_idx}_{c_idx}", on_click=evaluate_calc, use_container_width=True)
                    elif char == " " or char == "":
                        st.write("")
                    else:
                        st.button(char, key=f"{unique_prefix}_{r_idx}_{c_idx}", on_click=append_calc, args=(char,), use_container_width=True)

    with calc_tabs[0]:
        render_calc_grid([
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"]
        ], "grid_basic")

    with calc_tabs[1]:
        render_calc_grid([
            ["sin(", "cos(", "tan(", "^"],
            ["√(", "ln(", "log(", "1/x"],
            ["π", "e", "x", "="]
        ], "grid_alg_trig")

    with calc_tabs[2]:
        render_calc_grid([
            ["d/dx", "∫", "lim", "∑"],
            ["μ", "σ", "x̄", "!"],
            ["Δ", "∇", "∞", " "]
        ], "grid_calc_stat")

    st.write("---")
    st.header(lang["ctrl_header"])
    st.info(lang["ctrl_info"])

    if st.button(lang["reset_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.shown_resources = set()
        st.session_state.calc_expression = ""
        st.session_state.survey_answered = False
        questions = load_survey_questions()
        st.session_state.survey_question = random.choice(questions)
        st.rerun()

# =====================================
# 5. MAIN CONTENT AREA
# =====================================
st.title("🐅 BC TigerMath AI")
st.caption(lang["caption"])

# =====================================
# 6. QUICK-LOAD PROBLEM STARTERS
# =====================================
st.markdown(lang["quick_title"])
col1, col2, col3, col4 = st.columns(4)

if col1.button(lang["ql_1_btn"], use_container_width=True): st.session_state.quick_prompt = lang["ql_1_msg"]
if col2.button(lang["ql_2_btn"], use_container_width=True): st.session_state.quick_prompt = lang["ql_2_msg"]
if col3.button(lang["ql_3_btn"], use_container_width=True): st.session_state.quick_prompt = lang["ql_3_msg"]
if col4.button(lang["ql_4_btn"], use_container_width=True): st.session_state.quick_prompt = lang["ql_4_msg"]

st.write("---")

# =====================================
# 7. CAMPUS DATABASE REPOSITORY LOAD (OPTIMIZED & CACHED)
# =====================================
@st.cache_data(ttl=3600)
def load_verified_campus_data():
    try:
        with open("benedict_info.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "No supplementary historical documents found."

campus_knowledge_base = load_verified_campus_data()

def get_math_resources(text):
    q = text.lower()
    resource_map = {
        "alg": [("Khan Academy Algebra", "https://www.khanacademy.org/math/algebra")],
        "deriv": [("Calculus Derivatives", "https://tutorial.math.lamar.edu/Classes/CalcI/DerivativeIntro.aspx")],
        "integ": [("Integration Guide", "https://tutorial.math.lamar.edu/Classes/CalcI/DefiniteIntegrals.aspx")],
        "stat": [("Khan Academy Stats", "https://www.khanacademy.org/math/statistics-probability")],
        "trig": [("Trigonometry Basics", "https://www.khanacademy.org/math/trigonometry")]
    }
    results = []
    for key, links in resource_map.items():
        if key in q:
            results.extend(links)
    return list(set(results))

# =====================================
# 8. SOCRATIC PROMPT ENGINE CONSTRUCT
# =====================================
custom_style_val = st.session_state.get("custom_style", "")
style_instruction = f"\n- PERSONALITY/TONE MODIFIER: Adhere to this specific presentation style or persona: {custom_style_val}." if custom_style_val else ""

SYSTEM_INSTRUCTION = f"""You are 'BC TigerMath AI', a strict Socratic mathematics tutor and the premier BC Math Specialist at Benedict College. Match the energy a person comes with, and add a little tiger pride and humor from time to time.{style_instruction}

CRITICAL LANGUAGE REQUIREMENT:
{lang["sys_prompt"]} Everything you output must strictly match this language constraint.

🔴 CAMPUS KNOWLEDGE EXCEPTION:
- If the user asks general questions about Benedict College, step out of math mode entirely.
- Answer these questions accurately using ONLY the information provided in the VERIFIED CAMPUS DATA below. Do NOT use the Socratic method for these topics.

📋 VERIFIED CAMPUS DATA FROM REPOSITORY:
{campus_knowledge_base}

📐 MATHEMATICS DIRECTIVES:
- CRITICAL DIRECTIVE: For all math problems, NEVER give the user the final solution or write out a complete step-by-step answer upfront. Your core job is to guide them to discover it.
1. Identify the next mathematical step internally, but only provide ONE small hint or ask ONE target question to guide the student.
2. If the user says they are completely stuck, provide a brief micro-explanation of the underlying rule.
3. Keep responses highly interactive and conversational. Never write long blocks of text.
4. If they make an error, point out the breakdown in logic gently.
5. Only confirm the final answer after they have calculated it themselves.
"""

# =====================================
# 9. RENDER EXISTING CHAT HISTORY & EMBEDDED SURVEY
# =====================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Strategically Embedded Survey Question ---
if len(st.session_state.messages) >= 4 and not st.session_state.survey_answered:
    with st.chat_message("assistant"):
        st.markdown(f"📊 **Quick Student Feedback Check-In:**\n\n*{st.session_state.survey_question}*")
        
        survey_response = st.text_input("Type your response here:", key="embedded_survey_input")
        
        if st.button("Submit Feedback", key="submit_survey_btn"):
            print("🟢 [BUTTON CLICKED] 'Submit Feedback' was triggered by user.")
            if survey_response.strip() != "":
                # 1. Save feedback to OneDrive & Google Sheets Cloud
                save_survey_feedback(st.session_state.survey_question, survey_response)
                
                # 2. Save conversation logs to OneDrive & Google Sheets Cloud
                log_conversation(st.session_state.messages)
                
                # Update status and force interface cleanup
                st.session_state.survey_answered = True
                print("🔄 Execution complete. Rerunning app interface to hide survey module.")
                st.rerun()
            else:
                st.warning("Please provide a response before submitting.")

# =====================================
# 10. INPUT & EXECUTION LAYER (WITH NATIVE HOVERING INPUT)
# =====================================
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
    sym_tabs = st.tabs(["Algebra", "Trig", "Calc/Stats"])
    
    with sym_tabs[0]:
        s_row1 = st.columns(6)
        s_row1[0].button("π", key="sym_pi", on_click=send_symbol_to_state, args=("π",), use_container_width=True)
        s_row1[1].button("√", key="sym_sqrt", on_click=send_symbol_to_state, args=("√(",), use_container_width=True)
        s_row1[2].button("²", key="sym_sq", on_click=send_symbol_to_state, args=("²",), use_container_width=True)
        s_row1[3].button("^", key="sym_pow", on_click=send_symbol_to_state, args=("^",), use_container_width=True)
        s_row1[4].button("±", key="sym_pm", on_click=send_symbol_to_state, args=("±",), use_container_width=True)
        s_row1[5].button("x", key="sym_x", on_click=send_symbol_to_state, args=("x",), use_container_width=True)
        
    with sym_tabs[1]:
        s_row2 = st.columns(5)
        s_row2[0].button("sin", key="sym_sin", on_click=send_symbol_to_state, args=("sin(",), use_container_width=True)
        s_row2[1].button("cos", key="sym_cos", on_click=send_symbol_to_state, args=("cos(",), use_container_width=True)
        s_row2[2].button("tan", key="sym_tan", on_click=send_symbol_to_state, args=("tan(",), use_container_width=True)
        s_row2[3].button("θ", key="sym_theta", on_click=send_symbol_to_state, args=("θ",), use_container_width=True)
        s_row2[4].button("°", key="sym_deg", on_click=send_symbol_to_state, args=("°",), use_container_width=True)

    with sym_tabs[2]:
        s_row3 = st.columns(6)
        s_row3[0].button("∫", key="sym_int", on_click=send_symbol_to_state, args=("∫",), use_container_width=True)
        s_row3[1].button("d/dx", key="sym_diff", on_click=send_symbol_to_state, args=("d/dx ",), use_container_width=True)
        s_row3[2].button("lim", key="sym_lim", on_click=send_symbol_to_state, args=("lim ",), use_container_width=True)
        s_row3[3].button("∑", key="sym_sigma", on_click=send_symbol_to_state, args=("∑",), use_container_width=True)
        s_row3[4].button("∞", key="sym_inf", on_click=send_symbol_to_state, args=("∞",), use_container_width=True)
        s_row3[5].button("Δ", key="sym_delta", on_click=send_symbol_to_state, args=("Δ",), use_container_width=True)

user_query = st.chat_input(lang["chat_placeholder"])

if st.session_state.quick_prompt:
    user_query = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if user_query:
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    formatted_messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION}
    ]
    
    for msg in st.session_state.messages[-6:]:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        seen_urls = set()

        user_resources = get_math_resources(user_query)
        if user_resources:
            full_response += "📚 **Quick References:**\n"
            for title, url in user_resources:
                full_response += f"• [{title}]({url})\n"
                seen_urls.add(url)
            full_response += "\n---\n\n"

        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            # 🚀 Primary Attempt: Try generating with the heavy 70B model
            try:
                response_stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=formatted_messages,
                    temperature=0.6,
                    stream=True
                )
            except Exception as model_error:
                error_str = str(model_error)
                # 🔄 Fallback Trigger: If hitting rate limits, gracefully switch to the high-limit 8B model
                if "429" in error_str or "rate_limit" in error_str.lower():
                    print("⚠️ [RATE LIMIT] 70B model capped. Automatically falling back to 8B model...")
                    response_stream = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=formatted_messages,
                        temperature=0.6,
                        stream=True
                    )
                else:
                    raise model_error

            for chunk in response_stream:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")

            ai_resources = get_math_resources(full_response)
            new_resources = [res for res in ai_resources if res[1] not in seen_urls]

            if new_resources:
                full_response += "\n\n---\n💡 **Related Study Guides based on our conversation:**\n"
                for title, url in new_resources:
                    full_response += f"• [{title}]({url})\n"

            response_placeholder.markdown(full_response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(lang["error_msg"])
            st.info(str(e))
