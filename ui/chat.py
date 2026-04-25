"""
AI Tutor Chat Page - Ask questions and get answers
"""

import streamlit as st
import time
import html as html_module
from utils.config import SUBJECTS, get_subject
import utils.database as db
from modules.ai_engine import ask_tutor
from modules.voice_engine import speak, listen_for_speech, is_tts_available, get_voice_status


def render_chat():
    """Render the AI tutor chat page."""
    st.markdown('<div class="page-title">🤖 Ask AI Tutor</div>', unsafe_allow_html=True)

    student = db.get_student()
    api_key = student.get("api_key", "") or ""
    name = student.get("name", "Student")

    import os as _os
    from modules.ai_engine import is_valid_gemini_key
    ai_active = is_valid_gemini_key(api_key) or is_valid_gemini_key(_os.environ.get("GEMINI_API_KEY", ""))

    # ── AI Status Banner ─────────────────────────────────────
    if ai_active:
        st.success("🟢 AI Tutor is **ACTIVE** (Gemini connected) — Ask me anything!")
    else:
        st.warning(
            "🟡 AI Tutor is running in **Basic Mode** (no API key). "
            "Add your Gemini API key in ⚙️ Settings for full AI power!"
        )

    # ── Settings Row ─────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        subject_names = ["🌟 General"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = ["general"] + [s["id"] for s in SUBJECTS]

        default_idx = 0
        cs = st.session_state.get("chat_subject", "general")
        if cs in subject_ids:
            default_idx = subject_ids.index(cs)

        sel = st.selectbox("📚 Ask about:", subject_names, index=default_idx, key="chat_subj_sel")
        subject_id = subject_ids[subject_names.index(sel)]
        st.session_state.chat_subject = subject_id

    with col2:
        voice_status = get_voice_status()
        voice_on = st.checkbox("🔊 Voice Reply", value=st.session_state.get("voice_enabled", False),
                               disabled=not voice_status["tts_available"],
                               key="voice_toggle",
                               help="Requires pyttsx3 library")
        st.session_state.voice_enabled = voice_on

    with col3:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            db.clear_chat_history(subject_id)
            if "chat_messages" in st.session_state:
                del st.session_state["chat_messages"]
            st.rerun()

    # ── Load Chat History ────────────────────────────────────
    if "chat_messages" not in st.session_state:
        history = db.get_chat_history(subject_id, limit=20)
        st.session_state.chat_messages = history if history else []

    # Auto-send if navigated from a topic pill click
    prefill = st.session_state.get("chat_prefill", "")
    if prefill:
        st.session_state.chat_prefill = ""
        if not st.session_state.chat_messages:
            st.session_state.chat_messages = []
        _process_message(prefill, subject_id, api_key)
        st.rerun()

    # Add welcome message if empty
    if not st.session_state.chat_messages:
        subj_name = get_subject(subject_id)["name"] if subject_id != "general" else "anything"
        welcome = (
            f"Hello {name}! 👋 I'm your AI Tutor!\n\n"
            f"I'm here to help you with **{subj_name}**. "
            f"Ask me to explain a concept, solve a problem, or help with homework!\n\n"
            f"💡 *Tip: You can ask things like:*\n"
            f"- 'What is photosynthesis?'\n"
            f"- 'Explain fractions with examples'\n"
            f"- 'What caused the fall of the Mauryan Empire?'\n"
            f"- 'Help me solve: 3x + 7 = 22'"
        )
        st.session_state.chat_messages = [{"role": "assistant", "message": welcome}]

    # ── Chat Display ─────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            role = msg.get("role", "user")
            text = msg.get("message", "")

            safe_text = html_module.escape(text)
            if role == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <div class="chat-avatar-user">👤</div>
                    <div class="chat-bubble-user">{safe_text}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <div class="chat-avatar-ai">🤖</div>
                    <div class="chat-bubble-ai">{safe_text}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Input Area ───────────────────────────────────────────
    st.markdown("---")

    # Voice input
    if voice_status["stt_available"] and voice_status.get("microphone"):
        if st.button("🎤 Speak Your Question", key="voice_input_btn", use_container_width=False):
            with st.spinner("🎤 Listening... Speak now!"):
                text, success, error = listen_for_speech(timeout=5, phrase_time_limit=15)
            if success and text:
                st.session_state.voice_input_text = text
                st.success(f"🎤 Heard: '{text}'")
            else:
                st.warning(f"🎤 {error}")

    # Text input
    voice_text = st.session_state.get("voice_input_text", "")
    st.session_state.voice_input_text = ""

    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Ask your question:",
                value=voice_text,
                placeholder="Type your question here... e.g. 'What is a cell?'",
                label_visibility="collapsed",
                key="chat_input"
            )
        with col_send:
            send_btn = st.form_submit_button("📤 Send", use_container_width=True)

    # Quick question suggestions
    st.markdown("**Quick Questions:**")
    quick_qs = _get_quick_questions(subject_id)
    q_cols = st.columns(len(quick_qs))
    for i, (col, q) in enumerate(zip(q_cols, quick_qs)):
        with col:
            if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                _process_message(q, subject_id, api_key)
                st.rerun()

    # Process submitted message
    if send_btn and user_input.strip():
        _process_message(user_input.strip(), subject_id, api_key)
        st.rerun()

    # ── Tutor Tips ───────────────────────────────────────────
    with st.expander("💡 Tips for asking good questions"):
        st.markdown("""
        **How to ask better questions:**
        - 📌 Be specific: Instead of "help me", say "Explain photosynthesis with an example"
        - 🔢 For math: Write out the full problem clearly
        - 📖 For essays: Tell me the topic and length required
        - 🌍 For history/geography: Mention the specific event or place
        - 💬 Ask follow-up questions: "Can you explain that more simply?"
        - 🎯 Ask for examples: "Give me 3 examples of this"
        """)


def _process_message(user_input, subject_id, api_key):
    """Process a user message and get AI response."""
    # Add user message to display
    st.session_state.chat_messages.append({
        "role": "user", "message": user_input
    })
    db.save_chat_message("user", user_input, subject_id)

    # Get context
    context = st.session_state.get("chat_context", "")

    # Get AI response
    history = [m for m in st.session_state.chat_messages[-10:]]

    response, used_ai = ask_tutor(
        question=user_input,
        subject=subject_id,
        chapter_context=context,
        history=history,
        api_key=api_key
    )

    # Add response
    st.session_state.chat_messages.append({
        "role": "assistant", "message": response
    })
    db.save_chat_message("assistant", response, subject_id)
    db.add_points(2)

    # Voice response if enabled
    if st.session_state.get("voice_enabled"):
        speak(response, enabled=True)


def _get_quick_questions(subject_id):
    """Get subject-specific quick question suggestions."""
    quick = {
        "mathematics": ["📐 Explain fractions", "🔢 What is algebra?", "📊 How to solve equations?"],
        "biology":     ["🌿 What is photosynthesis?", "🦠 Tell me about cells", "🌍 What is ecology?"],
        "physics":     ["⚡ What is force?", "💡 How does light travel?", "🔊 What is sound?"],
        "chemistry":   ["🧪 What is matter?", "⚗️ Explain elements", "🌊 What is a mixture?"],
        "history":     ["🏛️ Indus Valley Civilization", "👑 Mauryan Empire", "📜 What is democracy?"],
        "geography":   ["🌍 What is latitude?", "🗻 Tell me about Himalayas", "🌊 Major oceans"],
        "english":     ["📝 Explain nouns", "⏰ What are tenses?", "✍️ How to write an essay?"],
        "computer":    ["💻 What is a CPU?", "🖥️ Explain operating systems", "🌐 What is internet?"],
        "gk":          ["🇮🇳 National symbols of India", "🌍 World's highest mountain", "🏆 Famous inventions"],
        "ai_robotics": ["🤖 What is Artificial Intelligence?", "⚙️ How do robots work?", "🧠 What is machine learning?"],
        "general":     ["📚 Help me study", "🎯 Study tips", "🧠 Memory techniques"],
    }
    return quick.get(subject_id, quick["general"])
