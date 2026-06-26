import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import time

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
        "chat_placeholder": "Hi there! What math problem can I help you with today? 🐅",
        "sys_prompt": "You MUST respond ONLY in English.",
        "error_msg": "Authentication or API Error. Please check your system configuration.",
        "explore_header": "Explore Math Topics & Formulas",
        "select_area": "Select Math Area",
        "select_topic": "Select Topic",
        "explain_btn": "Explain"
    },
    "Español": {
        "caption": "Tu Especialista Matemático BC | Creado por Mark Wells y Jamazio Mcphee",
        "lang_prompt": "🌍 Selecciona tu idioma",
        "ctrl_header": "Panel de Control",
        "ctrl_info": "¡El Especialista Matemático BC está listo para ayudar!",
        "reset_btn": "Reiniciar Conversación",
        "chat_placeholder": "¡Hola! ¿Con qué problema de matemáticas te puedo ayudar hoy? 🐅",
        "sys_prompt": "Debes responder ÚNICAMENTE en español.",
        "error_msg": "Error de API o autenticación. Verifica la configuración de tu sistema.",
        "explore_header": "Explorar Temas y Fórmulas",
        "select_area": "Seleccionar Área",
        "select_topic": "Seleccionar Tema",
        "explain_btn": "Explicar"
    },
    "Français": {
        "caption": "Votre spécialiste mathématique BC | Créé par Mark Wells et Jamazio Mcphee",
        "lang_prompt": "🌍 Choisissez votre langue",
        "ctrl_header": "Panneau de Configuration",
        "ctrl_info": "Le spécialiste mathématique BC est prêt à vous aider !",
        "reset_btn": "Réinitialiser la Conversation",
        "chat_placeholder": "Bonjour ! Avec quel problème de mathématiques puis-je vous aider aujourd'hui ? 🐅",
        "sys_prompt": "Vous devez répondre UNIQUEMENT en français.",
        "error_msg": "Erreur d'authentification ou d
