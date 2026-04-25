"""
📸 AI Image Doubt Solver
========================
Student uploads a photo of a question (math problem, textbook excerpt, worksheet)
and Gemini Vision returns a step-by-step explanation in simple language.

No OCR step needed — Gemini 2.5 reads images natively.
"""

import io
import os
import html as html_module

import streamlit as st

import utils.database as db
from utils.config import SUBJECTS, get_subject
from modules.ai_engine import solve_image_doubt, is_valid_gemini_key
from modules.browser_voice import speak, render_replay_button, LANG_LABELS, LANG_CODES


MAX_IMAGE_BYTES = 6 * 1024 * 1024  # 6 MB
ACCEPTED_TYPES = ["png", "jpg", "jpeg", "webp"]
MIME_BY_EXT = {
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


def render_doubt_solver():
    st.markdown('<div class="page-title">📸 AI Doubt Solver</div>', unsafe_allow_html=True)

    student = db.get_student()
    api_key = student.get("api_key", "") or ""
    ai_active = is_valid_gemini_key(api_key) or is_valid_gemini_key(
        os.environ.get("GEMINI_API_KEY", "")
    )

    if not ai_active:
        st.warning(
            "🟡 The Doubt Solver needs a Gemini API key to read images. "
            "Add one in **⚙️ Settings → 🤖 AI Settings**."
        )

    st.markdown(
        """
        <div class="upload-banner">
            📷 <b>How it works:</b> snap a photo of any homework question, textbook problem,
            or math sum — the AI tutor will read it and explain step-by-step.<br>
            <span style="color:#636e72; font-size:0.9rem;">
                Tip: bright light + crop just the question = best results.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Top controls: subject hint + voice language ──────────
    col_subj, col_lang = st.columns([2, 1])
    with col_subj:
        subject_names = ["🌟 General"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = ["general"] + [s["id"] for s in SUBJECTS]
        sel = st.selectbox("📚 Subject hint (optional)", subject_names, index=0, key="ds_subj")
        subject_id = subject_ids[subject_names.index(sel)]
    with col_lang:
        cur_lang = st.session_state.get("voice_lang", "en-IN")
        lang_idx = LANG_CODES.index(cur_lang) if cur_lang in LANG_CODES else 0
        lang_label = st.selectbox("🌐 Voice language", LANG_LABELS, index=lang_idx, key="ds_lang_sel")
        st.session_state.voice_lang = LANG_CODES[LANG_LABELS.index(lang_label)]

    # ── Upload area ──────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload or take a photo of the question",
        type=ACCEPTED_TYPES,
        accept_multiple_files=False,
        key="ds_uploader",
        help="JPG / PNG / WEBP, up to 6 MB. On phones, your camera will open.",
    )

    extra_note = st.text_input(
        "Anything you'd like to tell the tutor? (optional)",
        placeholder="e.g. 'I don't understand step 3' or 'Why is the answer negative?'",
        key="ds_note",
    )

    # Validate
    if uploaded is not None:
        size = getattr(uploaded, "size", 0) or 0
        if size > MAX_IMAGE_BYTES:
            st.error(f"❌ That image is {size // 1024} KB — please upload one under 6 MB.")
            uploaded = None

    # Live preview of the selected image
    if uploaded is not None:
        st.image(uploaded, caption=uploaded.name, use_container_width=True)

    # Solve button
    solve_btn = st.button(
        "🧠 Solve this doubt",
        disabled=(uploaded is None or not ai_active),
        type="primary",
        use_container_width=True,
        key="ds_solve_btn",
    )

    if solve_btn and uploaded is not None:
        ext = (uploaded.name.rsplit(".", 1)[-1] if "." in uploaded.name else "jpeg").lower()
        mime_type = MIME_BY_EXT.get(ext, "image/jpeg")
        image_bytes = uploaded.getvalue()

        with st.spinner("📖 Reading your question and thinking…"):
            response, used_ai = solve_image_doubt(
                image_bytes=image_bytes,
                mime_type=mime_type,
                subject=subject_id,
                extra_note=extra_note,
                api_key=api_key,
            )

        # Save to history
        db.save_doubt(
            subject=subject_id,
            note=extra_note,
            ai_response=response,
            image_filename=uploaded.name,
            image_size_kb=len(image_bytes) // 1024,
        )

        # Cache for THIS render so we can show + replay
        st.session_state["ds_last_response"] = response
        st.session_state["ds_last_used_ai"] = used_ai

        # Auto-speak (gated on the global voice toggle from chat)
        if st.session_state.get("voice_enabled", True):
            speak(response, lang=st.session_state.get("voice_lang", "en-IN"))

    # ── Show last response ───────────────────────────────────
    last_response = st.session_state.get("ds_last_response", "")
    if last_response:
        st.markdown("### 🧠 Tutor's explanation")
        safe = html_module.escape(last_response).replace("\n", "<br>")
        st.markdown(
            f'<div class="solution-box">{safe}</div>',
            unsafe_allow_html=True,
        )
        col_replay, col_clear = st.columns([1, 1])
        with col_replay:
            render_replay_button(
                last_response,
                lang=st.session_state.get("voice_lang", "en-IN"),
                key="ds_replay",
            )
        with col_clear:
            if st.button("🗑️ Clear answer", key="ds_clear"):
                st.session_state.pop("ds_last_response", None)
                st.session_state.pop("ds_last_used_ai", None)
                st.rerun()

    # ── Doubt history ────────────────────────────────────────
    st.markdown("---")
    history = db.get_doubt_history(limit=10)
    if history:
        st.markdown("### 📜 Recent doubts")
        for row in history:
            subj = row.get("subject") or "general"
            subj_name = (get_subject(subj)["name"]
                         if subj != "general" else "General")
            d = row.get("doubt_date") or ""
            preview = (row.get("ai_response") or "")[:120].replace("\n", " ")
            label = f"📅 {d}  •  📚 {subj_name}  •  📝 {row.get('image_filename') or '—'}"
            with st.expander(label):
                st.markdown(f"**Note:** {row.get('note') or '—'}")
                st.markdown("**Tutor said:**")
                st.write(row.get("ai_response") or "")
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    render_replay_button(
                        row.get("ai_response") or "",
                        lang=st.session_state.get("voice_lang", "en-IN"),
                        key=f"ds_hist_replay_{row.get('id')}",
                    )
                with col_b:
                    if st.button("🗑️ Delete", key=f"ds_hist_del_{row.get('id')}"):
                        db.delete_doubt(row.get("id"))
                        st.rerun()
    else:
        st.caption("Your solved doubts will show up here.")

    # ── Tips ─────────────────────────────────────────────────
    with st.expander("💡 Tips for great photos"):
        st.markdown(
            "- Take the photo in **bright light**, avoid shadows.\n"
            "- **Crop** to just the one question you need help with.\n"
            "- Hold the phone **flat above** the page (not at an angle).\n"
            "- For math, make sure all numbers and signs are clearly visible.\n"
            "- If the AI says it can't read it, retake and try again."
        )
