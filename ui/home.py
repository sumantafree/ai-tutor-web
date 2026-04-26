"""
Home Page UI - Dashboard / Welcome screen
"""

import streamlit as st
import random
from datetime import date
from utils.config import get_subject, get_subjects
from utils.helpers import get_day_greeting, get_motivation, format_time, get_grade_emoji
import utils.database as db


def render_home():
    """Render the home dashboard."""
    SUBJECTS = get_subjects()  # 🧠 Live curriculum (Phase 4)

    student = db.get_student()
    name = student.get("name", "Student")
    avatar = student.get("avatar", "🎓")
    greeting = get_day_greeting()
    today = date.today().strftime("%A, %d %B %Y")
    streak = db.get_current_streak()
    points = db.get_total_points()
    study_time = db.get_total_study_time()
    badges = db.get_badges()
    completed_chapters = db.get_completed_chapters()

    # ── Top Banner ──────────────────────────────────────────
    st.markdown(f"""
    <div class="home-banner">
        <div class="banner-left">
            <div class="avatar-large">{avatar}</div>
            <div>
                <div class="greeting-text">{greeting}, {name}! 👋</div>
                <div class="date-text">📅 {today}</div>
                <div class="motivation">{get_motivation()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card stat-blue">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">{points}</div>
            <div class="stat-label">Total Points</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card stat-orange">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">{streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card stat-green">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{len(completed_chapters)}</div>
            <div class="stat-label">Chapters Done</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card stat-purple">
            <div class="stat-icon">⏱️</div>
            <div class="stat-value">{format_time(study_time)}</div>
            <div class="stat-label">Study Time</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Navigation ─────────────────────────────────────
    st.markdown('<div class="section-title">📌 What do you want to do today?</div>', unsafe_allow_html=True)

    nav_cols = st.columns(5)
    nav_items = [
        ("📖", "Learn",    "learn",    "#FF6B6B"),
        ("📝", "Practice", "practice", "#6C5CE7"),
        ("🎮", "Play",     "play",     "#00B894"),
        ("🤖", "Ask Tutor","chat",     "#45B7D1"),
        ("📊", "Progress", "progress", "#FDCB6E"),
    ]
    for col, (icon, label, page, color) in zip(nav_cols, nav_items):
        with col:
            if st.button(f"{icon}\n{label}", key=f"nav_{page}", use_container_width=True,
                         help=f"Go to {label}"):
                st.session_state.page = page
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Subjects Grid ────────────────────────────────────────
    st.markdown('<div class="section-title">📚 Choose a Subject</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    stats = db.get_subject_stats()

    for i, subj in enumerate(SUBJECTS):
        col = cols[i % 4]
        with col:
            subj_stat = stats.get(subj["id"], {})
            avg_score = subj_stat.get("avg_score", 0)
            quiz_count = subj_stat.get("quiz_count", 0)

            score_display = f"⭐ {avg_score:.0f}%" if quiz_count > 0 else "Start learning!"

            if st.button(
                f"{subj['icon']} {subj['name']}\n{score_display}",
                key=f"subj_{subj['id']}",
                use_container_width=True,
                help=f"Study {subj['name']}"
            ):
                st.session_state.page = "learn"
                st.session_state.selected_subject = subj["id"]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Badges & Today's Plan (side by side) ──────────
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<div class="section-title">🏅 Recent Badges</div>', unsafe_allow_html=True)
        if badges:
            badge_html = '<div class="badge-container">'
            for badge in badges[-6:]:
                badge_html += f'''<div class="badge-item" title="{badge['badge_name']}">
                    <span style="font-size:2rem">{badge['badge_icon']}</span>
                    <div class="badge-name">{badge['badge_name']}</div>
                </div>'''
            badge_html += '</div>'
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.info("🎯 Complete lessons and quizzes to earn badges!")

    with right_col:
        st.markdown('<div class="section-title">📅 Today\'s Study Plan</div>', unsafe_allow_html=True)
        today_str = str(date.today())
        today_plans = db.get_study_plan(today_str)

        if today_plans:
            for plan in today_plans[:4]:
                subj = get_subject(plan["subject"])
                done_icon = "✅" if plan["completed"] else "⭕"
                st.markdown(f"{done_icon} **{subj['icon']} {subj['name']}** — {plan['topic']} ({plan['duration_minutes']} min)")
        else:
            st.info("📅 Go to the Planner to create today's study plan!")
            if st.button("➕ Create Study Plan", key="create_plan_home"):
                st.session_state.page = "planner"
                st.rerun()

    # ── Weak Areas Alert ─────────────────────────────────────
    weak_areas = db.get_weak_areas()
    if weak_areas:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Areas Needing Revision</div>', unsafe_allow_html=True)
        for area in weak_areas[:3]:
            subj = get_subject(area["subject"])
            score = area["avg_score"]
            col_warn, col_btn = st.columns([4, 1])
            with col_warn:
                st.warning(
                    f"**{subj['icon']} {subj['name']} - {area['chapter_title']}** "
                    f"| Average score: {score:.0f}%"
                )
            with col_btn:
                if st.button("📖 Revise", key=f"home_revise_{area['subject']}_{area['chapter_title'][:8]}",
                             use_container_width=True):
                    st.session_state.page = "learn"
                    st.session_state.selected_subject = area["subject"]
                    st.rerun()
