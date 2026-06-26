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
        "error_msg": "Erreur d'authentification ou d'API. Veuillez vérifier votre configuration.",
        "explore_header": "Explorer les Sujets et Formules",
        "select_area": "Sélectionner le Domaine",
        "select_topic": "Sélectionner le Sujet",
        "explain_btn": "Expliquer"
    },
    "Deutsch": {
        "caption": "Ihr BC Mathematik-Spezialist | Erstellt von Mark Wells und Jamazio Mcphee",
        "lang_prompt": "🌍 Sprache auswählen",
        "ctrl_header": "Kontrollzentrum",
        "ctrl_info": "Der BC Mathematik-Spezialist ist authentifiziert und bereit zu helfen!",
        "reset_btn": "Konversation zurücksetzen",
        "chat_placeholder": "Hallo! Bei welchem Mathematikproblem kann ich heute helfen? 🐅",
        "sys_prompt": "Du musst AUSSCHLIESSLICH auf Deutsch antworten.",
        "error_msg": "Authentifizierungs- oder API-Fehler. Bitte überprüfe deine Systemkonfiguration.",
        "explore_header": "Mathe-Themen & Formeln Erkunden",
        "select_area": "Bereich Auswählen",
        "select_topic": "Thema Auswählen",
        "explain_btn": "Erklären"
    }
}

# =====================================
# 3. MATH TOPICS REPOSITORY
# =====================================
MATH_TOPICS = {
    "Algebra": ["Quadratic Formula", "Slope-Intercept Form", "Properties of Exponents", "Logarithm Rules", "Systems of Equations"],
    "Trigonometry": ["Pythagorean Identities", "Law of Sines", "Law of Cosines", "Unit Circle Basics"],
    "Calculus": ["Limits Overview", "Power Rule (Derivatives)", "Product & Quotient Rules", "Integration by Parts", "Fundamental Theorem of Calculus"],
    "Statistics": ["Mean, Median, Mode", "Normal Distribution & Z-Scores", "Standard Deviation", "Bayes' Theorem"]
}

# =====================================
# 4. INITIALIZE SESSION STATE VARIABLES
# =====================================
if "language" not in st.session_state:
    st.session_state.language = "English"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "shown_resources" not in st.session_state:
    st.session_state.shown_resources = set()
if "custom_style" not in st.session_state:
    st.session_state.custom_style = ""
if "target_symbol" not in st.session_state:
    st.session_state.target_symbol = None

# --- NEW: Walkthrough State Trackers ---
if "is_in_walkthrough" not in st.session_state:
    st.session_state.is_in_walkthrough = False
if "walkthrough_step" not in st.session_state:
    st.session_state.walkthrough_step = 0
if "active_guide" not in st.session_state:
    st.session_state.active_guide = ""

lang = UI_TEXT.get(st.session_state.language, UI_TEXT["English"])

def send_symbol_to_state(symbol):
    st.session_state.target_symbol = symbol

# =====================================
# 5. SIDEBAR CONFIGURATION
# =====================================
with st.sidebar:
    st.header("📖 Training Guides")
    
    # --- UPDATED: Walkthrough Triggers ---
    if st.button("🎓 Student Guide Walkthrough", use_container_width=True):
        st.session_state.is_in_walkthrough = True
        st.session_state.walkthrough_step = 1
        st.session_state.active_guide = "Student Training Guide"
        st.session_state.messages.append({"role": "user", "content": "I would like to start the Student Training Guide walkthrough. Please give me Slide 1."})
        st.rerun()
        
    if st.button("👩‍🏫 Faculty Guide Walkthrough", use_container_width=True):
        st.session_state.is_in_walkthrough = True
        st.session_state.walkthrough_step = 1
        st.session_state.active_guide = "Faculty Training Guide"
        st.session_state.messages.append({"role": "user", "content": "I would like to start the Faculty Training Guide walkthrough. Please give me Slide 1."})
        st.rerun()

    st.write("---")

    with st.expander("🌍 Language & Style Settings", expanded=False):
        st.radio("Choose Language", list(UI_TEXT.keys()), key="language")
        st.text_input("🎭 Custom Persona / Style:", placeholder="e.g., Southern style, surfer slang...", key="custom_style")

    st.write("---")
    st.header(lang["ctrl_header"])
    st.info(lang["ctrl_info"])

    if st.button(lang["reset_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.shown_resources = set()
        st.session_state.is_in_walkthrough = False
        st.session_state.walkthrough_step = 0
        st.rerun()

# =====================================
# 6. MAIN CONTENT AREA
# =====================================
st.title("🐅 BC TigerMath AI")
st.caption(lang["caption"])
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
# 10. INTERACTIVE TOPIC EXPLORER
# =====================================
with st.expander(f"📚 {lang['explore_header']}", expanded=False):
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        selected_area = st.selectbox(lang["select_area"], list(MATH_TOPICS.keys()))
    with t_col2:
        selected_topic = st.selectbox(lang["select_topic"], MATH_TOPICS[selected_area])
        
    if st.button(f"{lang['explain_btn']} {selected_topic}", use_container_width=True):
        # Auto-cancel walkthrough if they jump to a math topic
        st.session_state.is_in_walkthrough = False 
        st.session_state.messages.append({
            "role": "user",
            "content": f"Can you give me the core formula and a brief conceptual explanation of how to approach: {selected_topic}?"
        })
        st.rerun()

# =====================================
# 11. INPUT & EXECUTION LAYER 
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

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    execute_ai = True
elif user_query:
    # --- NEW: Walkthrough progression logic ---
    if st.session_state.is_in_walkthrough:
        if any(word in user_query.lower() for word in ["stop", "exit", "cancel", "done", "math"]):
            st.session_state.is_in_walkthrough = False
        elif any(word in user_query.lower() for word in ["next", "continue", "yes", "ready"]):
            st.session_state.walkthrough_step += 1
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    execute_ai = True
else:
    execute_ai = False

if execute_ai:
    custom_style_val = st.session_state.get("custom_style", "")
    style_instruction = f"\n- PERSONALITY: {custom_style_val}." if custom_style_val else ""
    
    campus_context = ""
    if any(kw in user_query.lower() for kw in ["benedict", "college", "campus", "bc ", "tiger", "history", "founded", "faculty"]):
        campus_context = f"""
🔴 CAMPUS KNOWLEDGE EXCEPTION:
- Answer general questions about Benedict College accurately using the VERIFIED CAMPUS DATA below.
{campus_knowledge_base}"""

    # --- NEW: Inject hidden context so the LLM knows it's doing a walkthrough ---
    walkthrough_directive = ""
    if st.session_state.is_in_walkthrough:
        walkthrough_directive = f"""
🔴 WALKTHROUGH MODE ACTIVE:
You are currently guiding the user through the {st.session_state.active_guide}. They are on Slide {st.session_state.walkthrough_step}.
- Break the document into logical sections (Slide 1, Slide 2, etc.).
- ONLY provide the content for Slide {st.session_state.walkthrough_step}. Do NOT output the entire document.
- Keep the slide concise and formatted cleanly with headers.
- End your response by asking the user to type "Next" when they are ready to proceed.
"""

    SYSTEM_INSTRUCTION = f"""You are 'BC TigerMath AI', a strict Socratic mathematics tutor and the premier BC Math Specialist at Benedict College. Match the energy a person comes with, and add a little tiger pride and humor from time to time.{style_instruction}

📋 TRAINING GUIDES:
STUDENT GUIDE: {student_training_guide}
FACULTY GUIDE: {faculty_training_guide}

CRITICAL LANGUAGE REQUIREMENT:
{lang["sys_prompt"]}
{campus_context}
{walkthrough_directive}

📐 MATHEMATICS DIRECTIVES:
- CRITICAL MATH FORMATTING: Streamlit's math parser will break if you format math poorly. You MUST adhere to these exact rules:
  1. ALWAYS put display equations ($$) on their own separate lines, surrounded by blank lines. 
  2. NEVER put regular conversational text inside a LaTeX block.
  3. ALWAYS ensure block environments like \\begin{{aligned}} have a matching \\end{{aligned}}. Do not output partial or broken LaTeX.
- EXPLAINING FORMULAS: When the user asks for a formula, introduce it briefly, skip a line, write the formula cleanly in ($$) block format, skip another line, and then provide your conceptual breakdown. 
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
        if msg["role"] == "user" or (msg["role"] == "assistant" and not msg["content"].startswith("📚 **Quick References:**")):
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    # --- INJECTING HIDDEN PROMPT FOR WALKTHROUGH CONTINUATION ---
    if st.session_state.is_in_walkthrough and "next" in user_query.lower():
        formatted_messages[-1]["content"] += f"\n\n[SYSTEM NOTE: The user has requested the next slide. Please output Slide {st.session_state.walkthrough_step} of the {st.session_state.active_guide}.]"

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        scroll_placeholder = st.empty()
        full_response = ""
        seen_urls = set()

        user_resources = get_math_resources(user_query)
        if user_resources and not st.session_state.is_in_walkthrough:
            full_response += "📚 **Quick References:**\n"
            for title, url in user_resources:
                full_response += f"• [{title}]({url})\n"
                seen_urls.add(url)
            full_response += "\n---\n\n"

        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            response_stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=formatted_messages,
                temperature=0.6,
                stream=True
            )

            for chunk in response_stream:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    for char in content:
                        full_response += char
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.003)
                    
                    with scroll_placeholder:
                        components.html("""
                            <script>
                                var mainDoc = window.parent.document.querySelector('section.main');
                                if (mainDoc) { mainDoc.scrollTo(0, mainDoc.scrollHeight); }
                            </script>
                        """, height=0, width=0)

            ai_resources = get_math_resources(full_response)
            new_resources = [res for res in ai_resources if res[1] not in seen_urls]

            if new_resources and not st.session_state.is_in_walkthrough:
                full_response += "\n\n---\n💡 **Related Study Guides based on our conversation:**\n"
                for title, url in new_resources:
                    full_response += f"• [{title}]({url})\n"

            response_placeholder.markdown(full_response)
            scroll_placeholder.empty()

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(lang["error_msg"])
            st.info(str(e))
