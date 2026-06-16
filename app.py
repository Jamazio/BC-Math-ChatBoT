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
        "caption": "Votre spécialiste mathématique BC | Créé par Mark Wells y Jamazio Mcphee",
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
            st.session_state.calc_expression = st.session_state.
