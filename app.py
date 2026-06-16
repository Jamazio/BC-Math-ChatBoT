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

    /* Custom Design for the Calculator Grid Buttons */
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

    /* Accent lines and styling wrappers */
    div[data-testid="stSidebar"] { background-color: #1A1A1A; }
    div[data-testid="stChatInput"] { border: 2px solid #4C145E !important; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# =====================================
# 2. MULTI-LANGUAGE UI DICTIONARY
# =====================================
UI_TEXT = {
    "English": {
        "caption": "Your Campus BC Math Specialist | Created by Mark Wells and Jamazio Mcphee",
        "lang_prompt": "🌍 Select Your Language",
        "calc_header": "🧮 Equation Builder",
        "calc_caption": "Build your expression here, then copy it to the chat!",
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
        "calc_header": "🧮 Constructor de Ecuaciones",
        "calc_caption": "¡Construye tu expresión aquí y cópiala al chat!",
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

# Fallback safely to English if language selection drops out
lang = UI_TEXT.get(st.session_state.language, UI_TEXT["English"])

# =====================================
# 4. SIDEBAR CONFIGURATION (EQUATION BUILDER)
# =====================================
with st.sidebar:
    st.radio(
        "🌍 Choose Language",
        ["English", "Español"],
        key="language"
    )

    st.text_input(
        "🎭 Custom Persona / Style:",
        placeholder="e.g., Southern style, hyper energetic...",
        key="custom_style"
    )

    st.write("---")

    st.header(lang["calc_header"])
    st.caption(lang["calc_caption"])

    # Core Action Logic
    def append_calc(char):
        if st.session_state.calc_expression in ["Error", "0"]:
            st.session_state.calc_expression = ""
        st.session_state.calc_expression += str(char)

    def clear_calc():
        st.session_state.calc_expression = ""

    def evaluate_calc():
        try:
            expr = st.session_state.calc_expression
            if not expr:
                return

            expr = expr.replace("×", "*").replace("÷", "/")
            expr = expr.replace("π", "pi").replace("e", "e")
            expr = expr.replace("√(", "sqrt(")

            # Auto implicit multiplication
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

    # 🎛️ Row setup for Equation Display & Clear 'X' Button
    display_col, clear_col = st.columns([4, 1])
    with display_col:
        st.text_input(
            label="Equation Workspace",
            value=st.session_state.calc_expression,
            placeholder="Press Enter to apply",
            disabled=True,
            label_visibility="collapsed"
        )
    with clear_col:
        st.button("❌", key="clear_workspace_btn", on_click=clear_calc, use_container_width=True)

    # Tabs config customized to match uploaded imagery perfectly
    calc_tabs = st.tabs(["➕ Alg", "📈 Calc", "📊 Stat", "📐 Trig"])

    def render_calc_grid(buttons, unique_prefix):
        for r_idx, row in enumerate(buttons):
            cols = st.columns(len(row))
            for c_idx, char in enumerate(row):
                with cols[c_idx]:
                    if char == " " or char == "":
                        st.write("") 
                    else:
                        st.button(char, key=f"{unique_prefix}_{r_idx}_{c_idx}", on_click=append_calc, args=(char,), use_container_width=True)

    # Tab 1: Algebra Grid (Matching image_69f3ba.png layout)
    with calc_tabs[0]:
        render_calc_grid([
            ["+", "-", "×", "÷"],
            ["=", "≠", "x²", "x³"],
            ["xⁿ", "√", "∛", "()"],
            ["[]", "|x|", "∞", "½"]
        ], "grid_alg")

    # Tab 2: Calculus Grid
    with calc_tabs[1]:
        render_calc_grid([
            ["d/dx", "∫", "lim", "Δ"],
            ["∇", "ℹ", "", ""]
        ], "grid_calc")

    # Tab 3: Stats Grid
    with calc_tabs[2]:
        render_calc_grid([
            ["μ", "σ", "x̄", "!"],
            ["P(A)", "📊", "", ""]
        ], "grid_stat")

    # Tab 4: Trigonometry Grid
    with calc_tabs[3]:
        render_calc_grid([
            ["sin(", "cos(", "tan(", "^"],
            ["arcsin", "arccos", "arctan", "1/x"]
        ], "grid_trig")

    st.write("---")
    st.header(lang["ctrl_header"])
    st.info(lang["ctrl_info"])

    # 🛠️ FIXED: Typo line 209 completely repaired here:
    if st.button(lang["reset_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.shown_resources = set()
        st.session_state.calc_expression = ""
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
# 10. INPUT & EXECUTION LAYER
# =====================================
user_query = st.chat_input(lang["chat_placeholder"])

if st.session_state.quick_prompt:
    user_query = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(user_query)

    formatted_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in st.session_state.messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

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

        except Exception as e:
            st.error(lang["error_msg"])
            st.info(str(e))
        
