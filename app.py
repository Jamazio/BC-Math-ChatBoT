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
        "calc_caption": "Calculez des expressions de tous niveaux depuis la barre latérale !",
        "ctrl_header": "Panneau de Configuration",
        "ctrl_info": "Le spécialiste mathématique BC est prêt à vous aider !",
        "reset_btn": "Réinitialiser la Conversation",
        "quick_title": "**Démarreurs Rapides de Problèmes :**",
        "ql_1_btn": "➕ Algèbre",
        "ql_1_msg": "Comment résoudre une équation quadratique comme x² - 5x + 6 = 0 ?",
        "ql_2_btn": "📐 Pré-Calcul",
        "ql_2_msg": "Pouvez-vous m'aider à trouver la valeur exacte de sin(π/3) ?",
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
        "ql_4_msg": "Wie berechne ich die Standardabweichung oder den Z-Wert eines Datensatzes?",
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

# Load active language dictionary
lang = UI_TEXT[st.session_state.language]

# =====================================
# 4. SIDEBAR CONFIGURATION (CALCULATOR)
# =====================================
with st.sidebar:
    st.radio(
        "🌍 Choose Language",
        ["English", "Español", "Français", "Deutsch"],
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
        # If user clicks 1/x, append a structured reciprocal fraction syntax
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

            # Replace clean visual symbols with math operators
            expr = expr.replace("×", "*").replace("÷", "/")
            expr = expr.replace("π", "math.pi").replace("e", "math.e")

            # 🛠️ FIX: Smart Regex Parsing for Implicit Multiplication (e.g., "8tan(" -> "8*tan(")
            # Rule A: Insert '*' between a digit/constant and a letter or opening parenthesis
            expr = re.sub(r'(\d|math\.pi|math\.e)\s*([a-zA-Z\(])', r'\1*\2', expr)
            # Rule B: Insert '*' between a closing parenthesis and a digit/letter
            expr = re.sub(r'([\)])\s*([0-9a-zA-Z\(])', r'\1*\2', expr)

            # Map mathematical function strings directly to Python's math library execution
            expr = expr.replace("sin(", "math.sin(").replace("cos(", "math.cos(").replace("tan(", "math.tan(")
            expr = expr.replace("√(", "math.sqrt(").replace("ln(", "math.log(").replace("log(", "math.log10(")
            expr = expr.replace("^", "**")
            
            # 🛠️ FIX: Auto-close trailing parenthetical statements to prevent unclosed bracket syntax errors
            open_brackets = expr.count("(")
            close_brackets = expr.count(")")
            if open_brackets > close_brackets:
                expr += ")" * (open_brackets - close_brackets)

            # Context scope execution dictionary environments
            allowed_env = {"math": math, "__builtins__": None}
            result = eval(expr, allowed_env, {})
            
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            st.session_state.calc_expression = str(result)
        except Exception:
            st.session_state.calc_expression = "Error"

    # 🎛️ Calculator Interactive Display Screen
    st.text_input(
        label="Calculator Screen",
        value=st.session_state.calc_expression if st.session_state.calc_expression else "0",
        disabled=True,
        label_visibility="collapsed"
    )

    # Master Top Row Layout Controls
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        st.button("CLR", key="btn_master_clr", on_click=clear_calc, use_container_width=True)
    with ctrl_col2:
        st.button("DEL", key="btn_master_del", on_click=delete_last_calc, use_container_width=True)
    with ctrl_col3:
        st.button("(", key="btn_master_lparen", on_click=append_calc, args=("(",), use_container_width=True)
    with ctrl_col4:
        st.button(")", key="btn_master_rparen", on_click=append_calc, args=(")",), use_container_width=True)

    # Calculator Level Distribution Tabs
    calc_tabs = st.tabs(["🔢 Basic", "📐 Alg/Trig", "📈 Calc/Stat"])

    # UI Rendering grid generator
    def render_calc_grid(buttons, unique_prefix):
        for r_idx, row in enumerate(buttons):
            cols = st.columns(len(row))
            for c_idx, char in enumerate(row):
                with cols[c_idx]:
                    if char == "=":
                        st.button(char, key=f"{unique_prefix}_{r_idx}_{c_idx}", on_click=evaluate_calc, use_container_width=True)
                    elif char == " ":
                        st.write("") 
                    else:
                        st.button(char, key=f"{unique_prefix}_{r_idx}_{c_idx}", on_click=append_calc, args=(char,), use_container_width=True)

    # Tab 1: Arithmetic & Fractions
    with calc_tabs[0]:
        render_calc_grid([
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"]
        ], "grid_basic")

    # Tab 2: Algebra, Trigonometry & Fraction Templates
    with calc_tabs[1]:
        render_calc_grid([
            ["sin(", "cos(", "tan(", "^"],
            ["√(", "ln(", "log(", "1/x"],
            ["π", "e", "x", "="]
        ], "grid_alg_trig")

    # Tab 3: Calculus & Advanced Statistics Symbols
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

def get_math_resources(text):
    q = text.lower()
    resource_map = {
        "alg": [("Khan Academy Algebra", "https://www.khanacademy.org/math/algebra")],
        "equat": [("Solving Equations Guide", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:solve-equations-inequalities")],
        "solve": [("Equation Solver Tips", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:solve-equations-inequalities")],
        "slope": [("Slope & Linear Equations", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:forms-of-linear-equations")],
        "graph": [("Desmos Graphing Calculator", "https://www.desmos.com/calculator")],
        "polynom": [("Polynomials Overview", "https://www.khanacademy.org/math/algebra2/x2ec2f6f830c9fb89:poly-arithmetic")],
        "quadrat": [("Quadratic Functions", "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:quadratic-functions-equations")],
        "fraction": [("Fractions Help", "https://www.khanacademy.org/math/arithmetic/fraction-arithmetic")],
        "calc": [("Khan Academy Calculus", "https://www.khanacademy.org/math/calculus-1")],
        "deriv": [
            ("Khan Academy Derivatives", "https://www.khanacademy.org/math/differential-calculus"),
            ("Paul’s Calculus Notes", "https://tutorial.math.lamar.edu/Classes/CalcI/DerivativeIntro.aspx")
        ],
        "integ": [
            ("Khan Academy Integrals", "https://www.khanacademy.org/math/integral-calculus"),
            ("Paul’s Integration Guide", "https://tutorial.math.lamar.edu/Classes/CalcI/DefiniteIntegrals.aspx")
        ],
        "limit": [("Calculus Limits", "https://www.khanacademy.org/math/ap-calculus-ab/ab-limits-new")],
        "trig": [
            ("Khan Academy Trigonometry", "https://www.khanacademy.org/math/trigonometry"),
            ("Paul’s Online Notes - Trig", "https://tutorial.math.lamar.edu/Classes/Alg/TrigIntro.aspx")
        ],
        "geom": [("Khan Academy Geometry", "https://www.khanacademy.org/math/geometry")],
        "sin": [("Trig Ratios (Sine/Cosine/Tan)", "https://www.khanacademy.org/math/trigonometry/trigonometry-right-triangles")],
        "cos": [("Trig Ratios (Sine/Cosine/Tan)", "https://www.khanacademy.org/math/trigonometry/trigonometry-right-triangles")],
        "tan": [("Trig Ratios (Sine/Cosine/Tan)", "https://www.khanacademy.org/math/trigonometry/trigonometry-right-triangles")],
        "stat": [
            ("Stat Trek", "https://stattrek.com/"),
            ("Khan Academy Stats", "https://www.khanacademy.org/math/statistics-probability")
        ],
        "prob": [("Probability Rules", "https://www.khanacademy.org/math/statistics-probability/probability-library")],
        "data": [("Data Distributions", "https://www.khanacademy.org/math/statistics-probability/displaying-describing-data")],
        "matrix": [("Linear Algebra & Matrices", "https://www.khanacademy.org/math/linear-algebra")],
        "matric": [("Linear Algebra & Matrices", "https://www.khanacademy.org/math/linear-algebra")],
        "vector": [("Vectors Guide", "https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces")]
    }

    raw_results = []
    for key, links in resource_map.items():
        if key in q:
            raw_results.extend(links)

    unique_results = []
    seen_urls = set()
    for title, url in raw_results:
        if url not in seen_urls:
            unique_results.append((title, url))
            seen_urls.add(url)
    return unique_results

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
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    formatted_messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION}
    ]
    for msg in st.session_state.messages:
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
