"""
Learn Page UI - Chapter learning mode with explanations, examples, key points
"""

import streamlit as st
import time
import html as html_module
from utils.config import SUBJECTS, SYLLABUS, get_subject
import utils.database as db
from modules.voice_engine import speak, is_tts_available


def render_learn():
    """Render the learning page."""

    st.markdown('<div class="page-title">📖 Learn</div>', unsafe_allow_html=True)

    # ── Subject Selector ─────────────────────────────────────
    subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
    subject_ids   = [s["id"] for s in SUBJECTS]

    # Pre-select if navigated from home
    default_idx = 0
    if st.session_state.get("selected_subject"):
        sid = st.session_state.selected_subject
        if sid in subject_ids:
            default_idx = subject_ids.index(sid)

    col1, col2 = st.columns([2, 3])
    with col1:
        selected_name = st.selectbox("📚 Choose Subject", subject_names, index=default_idx, key="learn_subject_sel")
        selected_idx = subject_names.index(selected_name)
        subject_id = subject_ids[selected_idx]
        st.session_state.selected_subject = subject_id

    # Get chapters for selected subject
    subj = get_subject(subject_id)
    subj_data = SYLLABUS.get(subject_id, {})
    chapters = subj_data.get("chapters", [])

    if not chapters:
        # Check for uploaded content
        uploaded = db.get_uploaded_content(subject_id)
        if uploaded:
            st.info(f"📤 You have {len(uploaded)} uploaded file(s) for {subj['name']}. "
                    f"Questions can be generated in the Practice section.")
            _show_uploaded_content(subject_id, uploaded)
        else:
            st.info(f"📤 No built-in chapters for this subject yet. "
                    f"Upload your textbook in the Upload section!")
        return

    with col2:
        chapter_titles = [f"Chapter {ch['id']}: {ch['title']}" for ch in chapters]
        selected_chapter_label = st.selectbox("📑 Choose Chapter", chapter_titles, key="learn_chapter_sel")
        selected_chapter_idx = chapter_titles.index(selected_chapter_label)
        chapter = chapters[selected_chapter_idx]

    # ── Completed status ─────────────────────────────────────
    completed_chapters = {
        (c["subject"], c["chapter_id"])
        for c in db.get_completed_chapters(subject_id)
    }
    is_completed = (subject_id, chapter["id"]) in completed_chapters

    # ── Chapter Header ───────────────────────────────────────
    st.markdown(f"""
    <div class="chapter-header" style="background: {subj['bg']}; border-left: 5px solid {subj['color']}">
        <span style="font-size:2rem">{subj['icon']}</span>
        <div>
            <div class="chapter-title">{subj['name']} — Chapter {chapter['id']}</div>
            <div class="chapter-subtitle">{chapter['title']}</div>
        </div>
        {"<span class='completed-badge'>✅ Completed</span>" if is_completed else ""}
    </div>
    """, unsafe_allow_html=True)

    # ── Topics Covered ───────────────────────────────────────
    if chapter.get("topics"):
        st.markdown("**📋 Topics Covered:** *(click a topic to ask the AI Tutor about it)*")
        topics = chapter["topics"]
        topic_cols = st.columns(len(topics))
        for i, topic in enumerate(topics):
            with topic_cols[i]:
                if st.button(topic, key=f"topic_pill_{subject_id}_{chapter['id']}_{i}",
                             use_container_width=True):
                    st.session_state.page = "chat"
                    st.session_state.chat_subject = subject_id
                    st.session_state.chat_chapter = chapter['title']
                    st.session_state.chat_context = (
                        f"Chapter: {chapter['title']}\nTopic: {topic}"
                    )
                    st.session_state.chat_prefill = f"Please explain '{topic}' from {chapter['title']} in simple language for a Class 6 ICSE student."
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS: Explain / Key Points / Examples / Summary ──────
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Explanation", "🔑 Key Points", "💡 Examples", "📝 Summary Notes"])

    with tab1:
        _render_explanation(chapter, subj, subject_id)

    with tab2:
        _render_key_points(chapter, subj)

    with tab3:
        _render_examples(chapter, subj)

    with tab4:
        _render_summary(chapter, subject_id, subj)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Action Buttons ───────────────────────────────────────
    btn_cols = st.columns(3)
    with btn_cols[0]:
        if st.button("📝 Practice This Chapter", key="learn_practice_btn", use_container_width=True):
            st.session_state.page = "practice"
            st.session_state.practice_subject = subject_id
            st.session_state.practice_chapter = chapter["title"]
            st.rerun()

    with btn_cols[1]:
        if st.button("🤖 Ask AI Tutor", key="learn_ask_tutor", use_container_width=True):
            st.session_state.page = "chat"
            st.session_state.chat_subject = subject_id
            st.session_state.chat_chapter = chapter['title']
            st.session_state.chat_context = (
                f"Chapter: {chapter['title']}\n"
                f"Explanation: {chapter.get('explanation', '')[:500]}"
            )
            st.rerun()

    with btn_cols[2]:
        if not is_completed:
            if st.button("✅ Mark as Completed", key="learn_complete_btn", use_container_width=True):
                db.mark_chapter_complete(subject_id, chapter["id"], chapter["title"])
                db.log_study_session(subject_id, chapter["id"], chapter["title"], 20, "learn")
                db.add_points(50)
                st.success("🎉 Chapter marked as completed! +50 points!")
                st.balloons()
                time.sleep(1)
                st.rerun()
        else:
            st.success("✅ Chapter Completed!")


def _render_explanation(chapter, subj, subject_id):
    """Render the explanation tab."""
    student = db.get_student()
    api_key = student.get("api_key", "") or ""
    voice_enabled = st.session_state.get("voice_enabled", False)

    explanation = chapter.get("explanation", "")

    if explanation:
        st.markdown(f"""
        <div class="explanation-box" style="border-left: 4px solid {subj['color']}">
            {html_module.escape(explanation)}
        </div>
        """, unsafe_allow_html=True)

        if voice_enabled and is_tts_available():
            if st.button("🔊 Read Aloud", key="read_explanation"):
                speak(explanation, enabled=True)
                st.success("🔊 Reading aloud...")
    else:
        _show_uploaded_or_prompt(subject_id, chapter)

    # If API key available, show option to get AI explanation
    import os as _os
    from modules.ai_engine import is_valid_gemini_key
    _ai_on = is_valid_gemini_key(api_key) or is_valid_gemini_key(_os.environ.get("GEMINI_API_KEY", ""))
    if _ai_on:
        st.markdown("---")
        if st.button("🤖 Get AI-Enhanced Explanation", key="ai_explain"):
            with st.spinner("Getting AI explanation..."):
                from modules.ai_engine import ask_tutor
                prompt = f"Explain '{chapter['title']}' in simple language for a Class 6 ICSE student. Include examples and make it fun!"
                response, used_ai = ask_tutor(
                    prompt, subject_id, "", api_key=api_key,
                    chapter_title=chapter['title'],
                )
                st.markdown("### 🤖 AI Tutor Says:")
                st.markdown(response)


def _render_key_points(chapter, subj):
    """Render key points tab."""
    key_points = chapter.get("key_points", [])

    if key_points:
        st.markdown("### 🔑 Remember These Key Points!")
        for i, point in enumerate(key_points):
            color = subj["color"]
            st.markdown(f"""
            <div class="key-point-item" style="border-left: 3px solid {color}">
                <span class="kp-number">{i+1}</span>
                <span class="kp-text">{html_module.escape(point)}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>")
        st.info("💡 **Tip:** Read these key points out loud 3 times - it helps you remember them!")
    else:
        st.info("Key points will be available once you upload your textbook for this chapter.")


def _render_examples(chapter, subj):
    """Render examples tab."""
    examples = chapter.get("examples", [])

    if examples:
        st.markdown("### 💡 Let's Understand with Examples!")
        for i, example in enumerate(examples):
            st.markdown(f"""
            <div class="example-box" style="background: {subj['bg']}; border: 1px solid {subj['color']}">
                <span class="example-num">Example {i+1}</span>
                <p class="example-text">{html_module.escape(example)}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>")
        st.success("🌟 Great job reading the examples! Now try the practice questions!")
    else:
        st.info("Examples will be added as you upload textbook content.")


def _render_summary(chapter, subject_id, subj):
    """Render downloadable summary notes."""
    st.markdown("### 📝 Quick Summary Notes")

    title = chapter.get("title", "")
    explanation = chapter.get("explanation", "Not available yet")
    key_points = chapter.get("key_points", [])
    examples = chapter.get("examples", [])

    summary = f"# {title}\n\n"
    summary += f"## What is it?\n{explanation}\n\n"

    if key_points:
        summary += "## Key Points to Remember\n"
        for kp in key_points:
            summary += f"• {kp}\n"
        summary += "\n"

    if examples:
        summary += "## Examples\n"
        for i, ex in enumerate(examples, 1):
            summary += f"{i}. {ex}\n"
        summary += "\n"

    questions = chapter.get("questions", [])
    if questions:
        summary += "## Practice Questions\n"
        for i, q in enumerate(questions[:5], 1):
            summary += f"Q{i}. {q['q']}\nAns: {q['a']}\n\n"

    st.markdown(f"""
    <div class="summary-box">
        <pre style="white-space: pre-wrap; font-family: inherit;">{summary}</pre>
    </div>
    """, unsafe_allow_html=True)

    # Download button
    st.download_button(
        label="⬇️ Download Notes",
        data=summary,
        file_name=f"{subject_id}_{title.replace(' ', '_')}_notes.txt",
        mime="text/plain"
    )


def _show_uploaded_content(subject_id, uploaded_list):
    """Show list of uploaded files."""
    st.markdown("### 📤 Your Uploaded Materials")
    for item in uploaded_list:
        with st.expander(f"📄 {item['filename']} ({item['upload_date']})"):
            text = item.get("extracted_text", "")
            if text:
                st.text_area("Extracted Content (preview)", text[:1000] + ("..." if len(text) > 1000 else ""),
                             height=200, key=f"upload_preview_{item['id']}")


def _show_uploaded_or_prompt(subject_id, chapter):
    """Show uploaded content or prompt to upload."""
    uploaded = db.get_uploaded_content(subject_id)
    if uploaded:
        for item in uploaded[:1]:
            text = item.get("extracted_text", "")
            if text:
                st.markdown("**📤 Content from your uploaded book:**")
                preview = text[:800] + ("..." if len(text) > 800 else "")
                st.markdown(f"""
                <div class="explanation-box">
                    {html_module.escape(preview)}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(
            "📤 **Upload your textbook** in the Upload section to see the chapter content here!\n\n"
            "Go to: **Upload Materials** in the sidebar."
        )
