import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

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

    /* Accent lines and styling wrappers */
    div[data-testid="stSidebar"] { background-color: #1A1A1A; }
    div[data-testid="stChatInput"] { border: 2px solid #4C145E !important; border-radius: 12px; }
    
    /* Popover Menu Styling */
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
if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None
if "shown_resources" not in st.session_state:
    st.session_state.shown_resources = set()
if "custom_style" not in st.session_state:
    st.session_state.custom_style = ""
if "target_symbol" not in st.session_state:
    st.session_state.target_symbol = None

# Load active language dictionary dynamically
lang = UI_TEXT.get(st.session_state.language, UI_TEXT["English"])

# Callback to flag which symbol needs background injection
def send_symbol_to_state(symbol):
    st.session_state.target_symbol = symbol

# =====================================
# 4. SIDEBAR CONFIGURATION
# =====================================
with st.sidebar:
    # --- Training Guides ---
    st.header("📖 Training Guides")
    
    if st.button("🎓 Student Guide", use_container_width=True):
        st.session_state.quick_prompt = "Can you provide the Student Training Guide and explain how I can use TigerMath for my math lessons?"
        
    if st.button("👩‍🏫 Faculty Guide", use_container_width=True):
        st.session_state.quick_prompt = "Can you provide the Faculty Training Guide and explain how I can use TigerMath to create lesson plans?"

    st.write("---")

    # --- COLLAPSIBLE: Language & Persona Settings ---
    with st.expander("🌍 Language & Style Settings", expanded=False):
        st.radio(
            "Choose Language",
            list(UI_TEXT.keys()),
            key="language"
        )
        st.text_input(
            "🎭 Custom Persona / Style:",
            placeholder="e.g., Southern style, surfer slang...",
            key="custom_style"
        )

    st.write("---")
    st.header(lang["ctrl_header"])
    st.info(lang["ctrl_info"])

    if st.button(lang["reset_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.shown_resources = set()
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
# 8. PRE-LOAD TRAINING GUIDES
# =====================================
try:
    with open("student_guides.txt", "r", encoding="utf-8") as f:
        student_training_guide = f.read()
except:
    student_training_guide = "No student guide file found."

try:
    with open("faculty_guides.txt", "r", encoding="utf-8") as f:
        faculty_training_guide = f.read()
except:
    faculty_training_guide = "No faculty guide file found."

# =====================================
# 9. RENDER EXISTING CHAT HISTORY
# =====================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================
# 10. INPUT & EXECUTION LAYER 
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

    custom_style_val = st.session_state.get("custom_style", "")
    style_instruction = f"\n- PERSONALITY: {custom_style_val}." if custom_style_val else ""
    
    campus_context = ""
    if any(kw in user_query.lower() for kw in ["benedict", "college", "campus", "bc ", "tiger", "history", "founded", "faculty"]):
        campus_context = f"""
🔴 CAMPUS KNOWLEDGE EXCEPTION:
- Answer general questions about Benedict College accurately using the VERIFIED CAMPUS DATA below.
{campus_knowledge_base}"""

    SYSTEM_INSTRUCTION = f"""You are 'BC TigerMath AI', a strict Socratic mathematics tutor and the premier BC Math Specialist at Benedict College. Match the energy a person comes with, and add a little tiger pride and humor from time to time.{style_instruction}

📋 TRAINING GUIDES:
STUDENT GUIDE: {student_training_guide}
FACULTY GUIDE: {faculty_training_guide}

CRITICAL DIRECTIVE: When a user asks for these training guides, provide the content from the sections above. Do NOT say you do not have access.

CRITICAL LANGUAGE REQUIREMENT:
{lang["sys_prompt"]}
{campus_context}

📐 MATHEMATICS DIRECTIVES:
- MATH FORMATTING: You MUST use standard LaTeX formatting for all numbers, equations, fractions, limits, and powers. Wrap inline math in single dollar signs ($) and standalone equations in double dollar signs ($$). Never output raw math text like x^2, 3/4, or lim x->0.
- WHEN THE USER GETS IT RIGHT: Immediately validate them, say "Correct!" (or a warm equivalent), and ask what they want to tackle next. Do NOT serve up an unprompted mathematical problem or transition to another question automatically. Stop immediately and let the user decide.
- TONAL SENSITIVITY & EMBEDDED EMPATHY: NEVER use phrases like "easy", "simple", "easy peasy", "piece of cake", "basic", or imply a problem is trivial. Treat every math question with complete professional respect, validation, and encouragement. Never minimize the difficulty of any equation or concept.
- WHEN THE USER IS STUCK/LEARNING: NEVER give the final solution upfront. Guide them to discover it. Identify the next mathematical step internally, but only provide ONE small hint or ask ONE target question.
- If they make an error, point out the breakdown in logic gently.
- Keep responses highly interactive and conversational. Never write long blocks of text.
"""

    formatted_messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION}
    ]
    for msg in st.session_state.messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        seen_urls = set()
        user_resources = get_math_resources(user_query)
        prefix_text = ""
        
        # Display quick resources immediately if applicable
        if user_resources:
            prefix_text += "📚 **Quick References:**\n"
            for title, url in user_resources:
                prefix_text += f"• [{title}]({url})\n"
                seen_urls.add(url)
            prefix_text += "\n---\n\n"
            st.markdown(prefix_text)

        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            response_stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=formatted_messages,
                temperature=0.6,
                stream=True
            )

            # Generator to yield chunks for Streamlit's native typing effect
            def stream_generator():
                for chunk in response_stream:
                    content = getattr(chunk.choices[0].delta, "content", None)
                    if content:
                        yield content

            # st.write_stream automatically handles the typing cursor and auto-scrolling
            generated_text = st.write_stream(stream_generator())
            full_response = prefix_text + generated_text

            # Append new resources based on the AI's generated response
            ai_resources = get_math_resources(generated_text)
            new_resources = [res for res in ai_resources if res[1] not in seen_urls]

            if new_resources:
                suffix_text = "\n\n---\n💡 **Related Study Guides based on our conversation:**\n"
                for title, url in new_resources:
                    suffix_text += f"• [{title}]({url})\n"
                st.markdown(suffix_text)
                full_response += suffix_text

            # Save the complete response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(lang["error_msg"])
            st.info(str(e))
