"""
AI Tutor Chat Page - Ask questions and get answers (with browser-native voice).
"""

import os
import streamlit as st
import html as html_module
from utils.config import SUBJECTS, get_subject
import utils.database as db
from modules.ai_engine import ask_tutor, is_valid_gemini_key
from modules.browser_voice import (
    listen, speak, render_replay_button, LANG_LABELS, LANG_CODES,
)


def render_chat():
    """Render the AI tutor chat page."""
    st.markdown('<div class="page-title">🤖 Ask AI Tutor</div>', unsafe_allow_html=True)

    student = db.get_student()
    api_key = student.get("api_key", "") or ""
    name = student.get("name", "Student")

    ai_active = is_valid_gemini_key(api_key) or is_valid_gemini_key(
        os.environ.get("GEMINI_API_KEY", "")
    )

    # ── AI status banner ─────────────────────────────────────
    if ai_active:
        st.success("🟢 AI Tutor is **ACTIVE** (Gemini connected) — Ask me anything!")
    else:
        st.warning(
            "🟡 AI Tutor is running in **Basic Mode** (no API key). "
            "Add your Gemini API key in ⚙️ Settings for full AI power!"
        )

    # ── Settings row ─────────────────────────────────────────
    col_subj, col_lang, col_voice, col_clear = st.columns([2, 1.3, 1.2, 1])

    with col_subj:
        subject_names = ["🌟 General"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = ["general"] + [s["id"] for s in SUBJECTS]
        cs = st.session_state.get("chat_subject", "general")
        default_idx = subject_ids.index(cs) if cs in subject_ids else 0
        sel = st.selectbox("📚 Ask about:", subject_names, index=default_idx, key="chat_subj_sel")
        subject_id = subject_ids[subject_names.index(sel)]
        st.session_state.chat_subject = subject_id

    with col_lang:
        cur_lang = st.session_state.get("voice_lang", "en-IN")
        lang_idx = LANG_CODES.index(cur_lang) if cur_lang in LANG_CODES else 0
        lang_label = st.selectbox("🌐 Voice language:", LANG_LABELS, index=lang_idx, key="chat_lang_sel")
        st.session_state.voice_lang = LANG_CODES[LANG_LABELS.index(lang_label)]

    with col_voice:
        voice_on = st.checkbox(
            "🔊 Voice reply",
            value=st.session_state.get("voice_enabled", True),
            key="voice_toggle",
            help="Speak the AI's answer aloud using your browser.",
        )
        st.session_state.voice_enabled = voice_on

    with col_clear:
        st.write("")  # vertical align
        if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
            db.clear_chat_history(subject_id)
            st.session_state.pop("chat_messages", None)
            st.session_state.pop("speak_pending", None)
            st.rerun()

    # ── Load chat history ────────────────────────────────────
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

    # Welcome message if empty
    if not st.session_state.chat_messages:
        subj_name = get_subject(subject_id)["name"] if subject_id != "general" else "anything"
        welcome = (
            f"Hello {name}! 👋 I'm your AI Tutor!\n\n"
            f"I'm here to help you with **{subj_name}**. "
            f"Ask me to explain a concept, solve a problem, or help with homework!\n\n"
            f"💡 *Tip: You can type or tap the 🎤 microphone to speak.*"
        )
        st.session_state.chat_messages = [{"role": "assistant", "message": welcome}]

    # ── Chat display ─────────────────────────────────────────
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

    # 🔊 If a TTS line is pending (set by _process_message), speak it ONCE here.
    pending = st.session_state.pop("speak_pending", None)
    if pending and st.session_state.get("voice_enabled", True):
        speak(pending, lang=st.session_state.get("voice_lang", "en-IN"))

    # 🔊 Replay last assistant message
    last_ai_msg = next(
        (m["message"] for m in reversed(st.session_state.chat_messages)
         if m.get("role") == "assistant"),
        "",
    )
    if last_ai_msg:
        render_replay_button(last_ai_msg, lang=st.session_state.get("voice_lang", "en-IN"),
                             key="replay_last_ai")

    # ── Input area ───────────────────────────────────────────
    st.markdown("---")

    # 🎤 Browser-native mic (returns a transcript string when user finishes)
    transcript = listen(
        language=st.session_state.get("voice_lang", "en-IN"),
        key=f"mic_{subject_id}",
    )
    if transcript:
        st.success(f"🎤 Heard: '{transcript}'")
        _process_message(transcript, subject_id, api_key)
        st.rerun()

    # Text input
    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Ask your question:",
                value="",
                placeholder="Type your question here… or tap 🎤 above to speak.",
                label_visibility="collapsed",
                key="chat_input",
            )
        with col_send:
            send_btn = st.form_submit_button("📤 Send", use_container_width=True)

    # Quick suggestions
    st.markdown("**Quick Questions:**")
    quick_qs = _get_quick_questions(subject_id)
    q_cols = st.columns(len(quick_qs))
    for i, (col, q) in enumerate(zip(q_cols, quick_qs)):
        with col:
            if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                _process_message(q, subject_id, api_key)
                st.rerun()

    if send_btn and user_input.strip():
        _process_message(user_input.strip(), subject_id, api_key)
        st.rerun()

    with st.expander("💡 Tips for asking good questions"):
        st.markdown("""
        **How to ask better questions:**
        - 📌 Be specific: "Explain photosynthesis with an example"
        - 🔢 For math: write the full problem clearly
        - 📖 For essays: tell me the topic and length
        - 💬 Follow-ups work: "Can you explain that more simply?"
        - 🎤 Tap the mic and speak in English, Hindi or Bengali
        """)


def _process_message(user_input, subject_id, api_key):
    """Process a user message and get AI response."""
    st.session_state.chat_messages.append({"role": "user", "message": user_input})
    db.save_chat_message("user", user_input, subject_id)

    context = st.session_state.get("chat_context", "")
    history = list(st.session_state.chat_messages[-10:])

    response, _used_ai = ask_tutor(
        question=user_input,
        subject=subject_id,
        chapter_context=context,
        history=history,
        api_key=api_key,
    )

    st.session_state.chat_messages.append({"role": "assistant", "message": response})
    db.save_chat_message("assistant", response, subject_id)
    db.add_points(2)

    # Queue the response to be spoken on the NEXT render (gated by voice toggle there).
    st.session_state["speak_pending"] = response


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
