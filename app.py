import streamlit as st
from groq import Groq
import math
import re

# =====================================
# 1. PAGE SETUP & CONFIG
# =====================================
st.set_page_config(
    page_title="BC TigerMath AI", 
    page_icon="🐅", 
    layout="wide"
)

# --- 🎨 Custom CSS Injection: BC Purple & Tiger Gold Theme ---
st.markdown("""
    <style>
    /* Title and Subtitle Styling */
    h1 { 
        color: #FFD700 !important; 
        font-family: 'Arial Black', Gadget, sans-serif; 
    }
    .stCaption { 
        color: #F0F2F6 !important; 
        font-style: italic; 
    }

    /* Custom Design for the Calculator & Symbol Grid Buttons */
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

    /* Calculator Display Window Screen */
    input:disabled {
        background-color: #262730 !important;
        color: #FFD700 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
        text-align: right !important;
        opacity: 1 !important;
    }

    /* Custom Input Bar Styling (To look like a sleek native Chat Input) */
    div[data-testid="stTextInput"] input {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        border: 2px solid #4C145E !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.5) !important;
    }

    /* Accent lines and styling wrappers */
    div[data-testid="stSidebar"] { background-color: #1A1A1A; }
    div[data-testid="stPopover"] > button {
        background-color: #262730 !important;
        color: #FFD700 !important;
        border: 1px solid #4C145E !important;
        border-radius: 8px;
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
        "caption": "Votre spécialiste mathématique BC | Créé par Mark Wells et Jamazio Mcphee",
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
if "chat_draft" not in st.session_state:
    st.session_state.chat_draft = ""

# Load active language dictionary dynamically
lang = UI_TEXT.get(st.session_state.language, UI_TEXT["English"])

# Callback function to inject symbols directly into the text container
def append_symbol_to_chat(symbol):
    st.session_state.chat_draft += str(symbol)

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

    # Core Calculator Callbacks
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
        st.session_state.chat_draft = ""
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
# 7. CAMPUS DATABASE REPOSITORY LOAD
# =====================================
try:
    with open("benedict_info.txt", "r", encoding="utf-8") as file:
        campus_knowledge_base = file.read()
except FileNotFoundError:
    campus_knowledge_base = "No supplementary historical documents found."

# =====================================
# 8. SOCRATIC PROMPT ENGINE CONSTRUCT
# =====================================
style_instruction = f"\n- PERSONALITY/TONE MODIFIER: Adhere to this specific presentation style or persona: {st.session_state.custom_style}." if st.session_state.custom_style else ""
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
# 9. RENDER EXISTING CHAT HISTORY
# =====================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================
# 10. INPUT & EXECUTION LAYER (WITH CENGAGE CHART)
# =====================================

# Check for a Quick-Load bypass first
if st.session_state.quick_prompt:
    st.session_state.chat_draft = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

# Cengage-style Symbol Toolbar Tray using a compact popover layout
with st.popover("📐 Insert Math Symbols & Operations"):
    sym_tabs = st.tabs(["Algebra", "Trig", "Calc/Stats"])
    
    with sym_tabs[0]:
        s_row1 = st.columns(6)
        s_row1[0].button("π", key="sym_pi", on_click=append_symbol_to_chat, args=("π",), use_container_width=True)
        s_row1[1].button("√", key="sym_sqrt", on_click=append_symbol_to_chat, args=("√(",), use_container_width=True)
        s_row1[2].button("²", key="sym_sq", on_click=append_symbol_to_chat, args=("²",), use_container_width=True)
        s_row1[3].button("^", key="sym_pow", on_click=append_symbol_to_chat, args=("^",), use_container_width=True)
        s_row1[4].button("±", key="sym_pm", on_click=append_symbol_to_chat, args=("±",), use_container_width=True)
        s_row1[5].button("x", key="sym_x", on_click=append_symbol_to_chat, args=("x",), use_container_width=True)
        
    with sym_tabs[1]:
        s_row2 = st.columns(5)
        s_row2[0].button("sin", key="sym_sin", on_click=append_symbol_to_chat, args=("sin(",), use_container_width=True)
        s_row2[1].button("cos", key="sym_cos", on_click=append_symbol_to_chat, args=("cos(",), use_container_width=True)
        s_row2[2].button("tan", key="sym_tan", on_click=append_symbol_to_chat, args=("tan(",), use_container_width=True)
        s_row2[3].button("θ", key="sym_theta", on_click=append_symbol_to_chat, args=("θ",), use_container_width=True)
        s_row2[4].button("°", key="sym_deg", on_click=append_symbol_to_chat, args=("°",), use_container_width=True)

    with sym_tabs[2]:
        s_row3 = st.columns(6)
        s_row3[0].button("∫", key="sym_int", on_click=append_symbol_to_chat, args=("∫",), use_container_width=True)
        s_row3[1].button("d/dx", key="sym_diff", on_click=append_symbol_to_chat, args=("d/dx ",), use_container_width=True)
        s_row3[2].button("lim", key="sym_lim", on_click=append_symbol_to_chat, args=("lim ",), use_container_width=True)
        s_row3[3].button("∑", key="sym_sigma", on_click=append_symbol_to_chat, args=("∑",), use_container_width=True)
        s_row3[4].button("∞", key="sym_inf", on_click=append_symbol_to_chat, args=("∞",), use_container_width=True)
        s_row3[5].button("Δ", key="sym_delta", on_click=append_symbol_to_chat, args=("Δ",), use_container_width=True)

# Coordinated Chat Entry Row
input_col, action_col = st.columns([0.88, 0.12])

with input_col:
    user_query = st.text_input(
        label="Chat Input Field",
        value=st.session_state.chat_draft,
        placeholder=lang["chat_placeholder"],
        label_visibility="collapsed"
    )

with action_col:
    submit_triggered = st.button("Send 🚀", use_container_width=True)

# Processing Logic on submission execution
if submit_triggered and user_query:
    # Append user question to history tracking lists
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Reset layout values safely
    st.session_state.chat_draft = ""
    
    # Temporarily refresh view display to show state adjustments cleanly
    st.rerun()

# Run actual prompt inferences if history demands attention updates
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_user_message = st.session_state.messages[-1]["content"]
    
    formatted_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in st.session_state.messages[:-1]:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})
    formatted_messages.append({"role": "user", "content": current_user_message})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response_stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=formatted_messages,
                temperature=0.6,
                stream=True
            )

            for chunk in response_stream:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()

        except Exception as e:
            st.error(lang["error_msg"])
            st.info(str(e))
