"""
📚 Admin: Curriculum Manager
============================
Parent-facing CRUD for the dynamic curriculum tree:

    Subjects → Chapters → Topics / Key points / Examples / Questions

All edits go to the `cur_subjects` / `cur_chapters` tables and are picked
up live by every consumer page (Learn, Practice, Chat, Doubt Solver, …)
on the next render.
"""

import streamlit as st
import utils.curriculum as cur


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────

def render_admin_curriculum():
    st.markdown('<div class="page-title">📚 Curriculum Manager</div>',
                unsafe_allow_html=True)

    st.caption(
        "Edit subjects, chapters, and topics. Changes appear instantly on "
        "Learn, Practice, Chat and Doubt Solver pages on the next render. "
        "All data is stored in your Supabase database."
    )

    tab_subjects, tab_chapters, tab_help = st.tabs([
        "📚 Subjects", "📑 Chapters & Topics", "❓ Help",
    ])

    with tab_subjects:
        _render_subjects_tab()

    with tab_chapters:
        _render_chapters_tab()

    with tab_help:
        _render_help_tab()


# ─────────────────────────────────────────────────────────
# SUBJECTS TAB
# ─────────────────────────────────────────────────────────

def _render_subjects_tab():
    st.markdown("### 📚 Subjects")

    subjects = cur.get_all_subjects()

    # ── Add new subject ────────────────────────────────────
    with st.expander("➕ Add new subject", expanded=False):
        with st.form("add_subject_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_name = st.text_input("Name *", placeholder="e.g. Sanskrit")
            with col2:
                new_icon = st.text_input("Icon (emoji)", value="📚", max_chars=4)
            col3, col4 = st.columns(2)
            with col3:
                new_color = st.color_picker("Primary color", value="#74B9FF")
            with col4:
                new_bg = st.color_picker("Background tint", value="#E5F4FB")

            if st.form_submit_button("➕ Add subject", use_container_width=True,
                                     type="primary"):
                if not new_name.strip():
                    st.error("Name is required.")
                else:
                    cur.add_subject(
                        name=new_name.strip(),
                        icon=new_icon or "📚",
                        color=new_color,
                        bg=new_bg,
                    )
                    st.success(f"✅ Added subject '{new_name}'.")
                    st.rerun()

    # ── Existing subjects ──────────────────────────────────
    if not subjects:
        st.info("No subjects yet. Add one above.")
        return

    for s in subjects:
        with st.expander(f"{s['icon']} {s['name']}  —  code: `{s['id']}`"):
            with st.form(f"edit_subject_{s['_db_id']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    e_name = st.text_input("Name", value=s["name"], key=f"sname_{s['_db_id']}")
                with col2:
                    e_icon = st.text_input("Icon", value=s["icon"], max_chars=4,
                                           key=f"sicon_{s['_db_id']}")
                col3, col4 = st.columns(2)
                with col3:
                    e_color = st.color_picker("Primary color", value=s["color"],
                                              key=f"scolor_{s['_db_id']}")
                with col4:
                    e_bg = st.color_picker("Background tint", value=s["bg"],
                                           key=f"sbg_{s['_db_id']}")

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    save = st.form_submit_button("💾 Save", use_container_width=True,
                                                 type="primary")
                with btn_col2:
                    delete = st.form_submit_button("🗑️ Delete subject",
                                                   use_container_width=True)

                if save:
                    cur.update_subject(
                        s["_db_id"], name=e_name, icon=e_icon,
                        color=e_color, bg=e_bg,
                    )
                    st.success("Saved.")
                    st.rerun()
                if delete:
                    st.session_state[f"_confirm_del_subj_{s['_db_id']}"] = True

            if st.session_state.get(f"_confirm_del_subj_{s['_db_id']}"):
                chs = cur.get_chapters_for(s["id"])
                st.warning(
                    f"⚠️ This will permanently delete **{s['name']}** and all "
                    f"{len(chs)} chapter(s) under it. This cannot be undone."
                )
                yes, no = st.columns(2)
                with yes:
                    if st.button("✅ Yes, delete it", key=f"del_yes_{s['_db_id']}",
                                 type="primary", use_container_width=True):
                        cur.delete_subject(s["_db_id"])
                        st.session_state.pop(f"_confirm_del_subj_{s['_db_id']}", None)
                        st.success("Deleted.")
                        st.rerun()
                with no:
                    if st.button("❌ Cancel", key=f"del_no_{s['_db_id']}",
                                 use_container_width=True):
                        st.session_state.pop(f"_confirm_del_subj_{s['_db_id']}", None)
                        st.rerun()


# ─────────────────────────────────────────────────────────
# CHAPTERS TAB
# ─────────────────────────────────────────────────────────

def _render_chapters_tab():
    st.markdown("### 📑 Chapters & Topics")

    subjects = cur.get_all_subjects()
    if not subjects:
        st.info("Add a subject first in the Subjects tab.")
        return

    subj_labels = [f"{s['icon']} {s['name']}" for s in subjects]
    subj_idx = st.selectbox(
        "Pick a subject to manage its chapters",
        options=list(range(len(subjects))),
        format_func=lambda i: subj_labels[i],
        key="adm_pick_subject",
    )
    subject = subjects[subj_idx]

    chapters = cur.get_chapters_for(subject["id"])

    # ── Add chapter ────────────────────────────────────────
    with st.expander(f"➕ Add new chapter to {subject['name']}", expanded=False):
        with st.form("add_chapter_form", clear_on_submit=True):
            new_title = st.text_input("Chapter title *",
                                      placeholder="e.g. Light and Shadows")
            new_explanation = st.text_area(
                "Short explanation (shown to the student)",
                placeholder="What is this chapter about? 2–4 sentences in simple language.",
                height=110,
            )
            new_topics = st.text_area(
                "Topics (one per line)",
                placeholder="Reflection\nRefraction\nUses of light",
                height=100,
            )
            new_keypoints = st.text_area(
                "Key points to remember (one per line)",
                placeholder="Light travels in a straight line.\nLight bounces off shiny surfaces.",
                height=100,
            )
            new_examples = st.text_area(
                "Real-life examples (one per line)",
                placeholder="A mirror reflects light.\nA pencil in water looks bent because of refraction.",
                height=80,
            )

            if st.form_submit_button("➕ Add chapter",
                                     use_container_width=True, type="primary"):
                if not new_title.strip():
                    st.error("Title is required.")
                else:
                    cur.add_chapter(
                        subject_db_id=subject["_db_id"],
                        title=new_title.strip(),
                        explanation=new_explanation.strip(),
                        topics=_split_lines(new_topics),
                        key_points=_split_lines(new_keypoints),
                        examples=_split_lines(new_examples),
                        questions=[],
                    )
                    st.success(f"✅ Added chapter '{new_title}'.")
                    st.rerun()

    if not chapters:
        st.info("No chapters yet for this subject. Add one above.")
        return

    st.markdown(f"#### {len(chapters)} chapter(s) in {subject['icon']} {subject['name']}")

    for ch in chapters:
        with st.expander(f"📑 {ch['title']}"):
            _render_chapter_editor(subject, ch)


def _render_chapter_editor(subject, chapter):
    db_id = chapter["_db_id"]

    with st.form(f"edit_chapter_{db_id}"):
        e_title = st.text_input("Title", value=chapter["title"],
                                key=f"ctitle_{db_id}")
        e_expl = st.text_area("Explanation",
                              value=chapter["explanation"],
                              height=110, key=f"cexpl_{db_id}")
        e_topics = st.text_area(
            "Topics (one per line)",
            value="\n".join(chapter.get("topics") or []),
            height=100, key=f"ctopics_{db_id}",
        )
        e_keypoints = st.text_area(
            "Key points (one per line)",
            value="\n".join(chapter.get("key_points") or []),
            height=100, key=f"ckp_{db_id}",
        )
        e_examples = st.text_area(
            "Examples (one per line)",
            value="\n".join(chapter.get("examples") or []),
            height=80, key=f"cex_{db_id}",
        )
        e_sort = st.number_input(
            "Sort order (lower shows first)",
            value=int(chapter.get("_sort_order") or 0),
            step=1, key=f"csort_{db_id}",
        )

        st.markdown("**Practice questions** (Q + A pairs)")
        questions = chapter.get("questions") or []
        # Render existing questions
        new_questions = []
        for i, q in enumerate(questions):
            qcol, acol = st.columns(2)
            with qcol:
                q_text = st.text_input(
                    f"Q{i+1}",
                    value=q.get("q", ""),
                    key=f"cq_{db_id}_{i}",
                )
            with acol:
                a_text = st.text_input(
                    f"A{i+1}",
                    value=q.get("a", ""),
                    key=f"ca_{db_id}_{i}",
                )
            if q_text.strip() and a_text.strip():
                new_questions.append({
                    "q": q_text.strip(),
                    "a": a_text.strip(),
                    "type": q.get("type", "short"),
                    "options": q.get("options", []),
                })

        # One blank row to add a new Q&A
        qcol, acol = st.columns(2)
        with qcol:
            extra_q = st.text_input(
                f"➕ New Q",
                value="",
                key=f"cq_new_{db_id}",
                placeholder="Type a new question…",
            )
        with acol:
            extra_a = st.text_input(
                f"➕ New A",
                value="",
                key=f"ca_new_{db_id}",
                placeholder="…and its answer.",
            )
        if extra_q.strip() and extra_a.strip():
            new_questions.append({
                "q": extra_q.strip(),
                "a": extra_a.strip(),
                "type": "short",
                "options": [],
            })

        save_col, delete_col = st.columns(2)
        with save_col:
            save = st.form_submit_button("💾 Save chapter",
                                         use_container_width=True, type="primary")
        with delete_col:
            delete = st.form_submit_button("🗑️ Delete chapter",
                                           use_container_width=True)

        if save:
            cur.update_chapter(
                db_id,
                title=e_title,
                explanation=e_expl,
                topics=_split_lines(e_topics),
                key_points=_split_lines(e_keypoints),
                examples=_split_lines(e_examples),
                questions=new_questions,
                sort_order=int(e_sort),
            )
            st.success("Saved.")
            st.rerun()

        if delete:
            st.session_state[f"_confirm_del_ch_{db_id}"] = True

    if st.session_state.get(f"_confirm_del_ch_{db_id}"):
        st.warning(f"⚠️ Permanently delete chapter **{chapter['title']}**?")
        yes, no = st.columns(2)
        with yes:
            if st.button("✅ Yes, delete", key=f"ch_del_yes_{db_id}",
                         type="primary", use_container_width=True):
                cur.delete_chapter(db_id)
                st.session_state.pop(f"_confirm_del_ch_{db_id}", None)
                st.success("Deleted.")
                st.rerun()
        with no:
            if st.button("❌ Cancel", key=f"ch_del_no_{db_id}",
                         use_container_width=True):
                st.session_state.pop(f"_confirm_del_ch_{db_id}", None)
                st.rerun()


# ─────────────────────────────────────────────────────────
# HELP TAB
# ─────────────────────────────────────────────────────────

def _render_help_tab():
    st.markdown("""
### How this works

The curriculum (subjects → chapters → topics) is now stored in your
**Supabase database**, not hardcoded. Every page that uses the syllabus
(Learn, Practice, Chat, Doubt Solver, Progress) reads it live, so any
edit you make here shows up immediately on the next page render.

**Tips:**

- **Topics, key points, examples** — one item per line. Empty lines are ignored.
- **Sort order** — lower numbers appear first. Use 1, 2, 3… to control order.
- **Delete** — irreversible. A confirm step is required.
- **Subject "code"** — auto-derived from the name on creation. Used internally
  by the database (don't worry about it).
- **First-time data** — the database was auto-seeded from the original
  hardcoded ICSE Class 6 syllabus. You can keep, edit, or delete any of it.

**What is NOT yet editable from this page:**

- The visual color picker writes the colors but the badges in the UI use a
  small fixed palette per subject. Visual style updates may take effect after
  a full app refresh.
- Question "type" (short / mcq / identify) — currently locked to `short`.
  MCQ option editing will come in a later release.
""")


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def _split_lines(text: str) -> list:
    """Convert a multi-line text area into a list of trimmed non-empty lines."""
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]
