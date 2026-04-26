"""
Study Planner Page UI
"""

import streamlit as st
from datetime import date, timedelta
from utils.config import get_subject, get_subjects
from utils.helpers import format_time
import utils.database as db
from modules.study_planner import generate_daily_plan, get_study_tips, get_revision_schedule


def render_planner():
    """Render the study planner page."""
    st.markdown('<div class="page-title">📅 Study Planner</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📅 Today's Plan", "📆 Weekly Planner", "💡 Study Tips"])

    with tab1:
        _render_today_plan()

    with tab2:
        _render_weekly_planner()

    with tab3:
        _render_study_tips()


def _render_today_plan():
    """Show today's study plan."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)
    today = str(date.today())
    today_display = date.today().strftime("%A, %d %B %Y")

    st.markdown(f"### 📅 {today_display}")

    today_plans = db.get_study_plan(today)

    if today_plans:
        completed = sum(1 for p in today_plans if p["completed"])
        total = len(today_plans)
        progress = completed / total if total > 0 else 0

        st.progress(progress, text=f"✅ {completed}/{total} tasks completed today")

        for plan in today_plans:
            subj = get_subject(plan["subject"])
            is_done = bool(plan["completed"])

            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                text = f"~~{subj['icon']} **{subj['name']}**: {plan['topic']}~~" if is_done else \
                       f"{subj['icon']} **{subj['name']}**: {plan['topic']}"
                st.markdown(text)
            with col2:
                priority_color = {"High": "🔴", "Normal": "🟡", "Low": "🟢"}
                priority = plan.get("priority", "Normal")
                st.markdown(f"{priority_color.get(priority, '🟡')} {priority} | ⏱️ {plan['duration_minutes']} min")
            with col3:
                if not is_done:
                    if st.button("✅ Done", key=f"done_{plan['id']}", use_container_width=True):
                        db.mark_plan_completed(plan["id"])
                        db.log_study_session(
                            plan["subject"], 0, plan["topic"],
                            plan["duration_minutes"], "planned"
                        )
                        st.success(f"✅ Great job! +20 points!")
                        st.rerun()
                else:
                    st.markdown("✅ Done!")
            with col4:
                if st.button("📖 Study", key=f"study_{plan['id']}", use_container_width=True):
                    st.session_state.page = "learn"
                    st.session_state.selected_subject = plan["subject"]
                    st.rerun()
    else:
        st.info("No study plan for today yet. Create one below or generate an auto plan!")

    # Add manual task
    st.markdown("---")
    st.markdown("#### ➕ Add a Task for Today")

    col1, col2, col3 = st.columns(3)
    with col1:
        subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = [s["id"] for s in SUBJECTS]
        sel = st.selectbox("📚 Subject", subject_names, key="add_task_subj")
        subject_id = subject_ids[subject_names.index(sel)]

    with col2:
        topic = st.text_input("📑 Topic", placeholder="e.g. Chapter 3: Fractions", key="add_task_topic")

    with col3:
        duration = st.number_input("⏱️ Minutes", min_value=10, max_value=120, value=30, step=10, key="add_task_dur")

    priority = st.select_slider("Priority", ["Low", "Normal", "High"], value="Normal", key="add_task_priority")

    if st.button("➕ Add Task", key="add_plan_task", use_container_width=True):
        if topic.strip():
            db.save_study_plan(today, subject_id, topic.strip(), duration, priority)
            st.success("✅ Task added to today's plan!")
            st.rerun()
        else:
            st.warning("Please enter a topic name!")


def _render_weekly_planner():
    """Create and view a weekly study plan."""
    st.markdown("### 📆 Weekly Study Plan")

    # Auto-generate plan
    st.markdown("#### 🤖 Auto-Generate Plan")
    st.info("Let the AI create a smart study plan based on your weak areas and syllabus!")

    col1, col2 = st.columns(2)
    with col1:
        study_days = st.selectbox("📅 Study Days per Week", [3, 5, 7], index=1, key="plan_days")
    with col2:
        daily_hours = st.selectbox("⏱️ Daily Study Hours", [1, 1.5, 2, 2.5, 3], index=1, key="plan_hours")

    if st.button("🤖 Generate 7-Day Plan", use_container_width=True, key="gen_plan"):
        weak_areas = db.get_weak_areas()
        with st.spinner("Generating your personalized study plan..."):
            plan_items = generate_daily_plan(
                weak_areas=weak_areas,
                study_days_per_week=study_days,
                daily_hours=daily_hours
            )

        if plan_items:
            for item in plan_items:
                db.save_study_plan(
                    item["date"], item["subject"], item["topic"],
                    item["duration_minutes"], item["priority"]
                )

            st.success(f"✅ Study plan created with **{len(plan_items)} sessions** over 7 days!")
            st.rerun()

    # Show weekly calendar
    st.markdown("---")
    st.markdown("#### 📅 This Week's Schedule")

    today = date.today()
    all_plans = db.get_study_plan()

    for day_offset in range(7):
        day = today + timedelta(days=day_offset)
        day_str = str(day)
        day_label = day.strftime("%A, %d %B")
        if day == today:
            day_label = f"**TODAY** - {day_label}"

        day_plans = [p for p in all_plans if p["plan_date"] == day_str]

        if day_plans:
            with st.expander(f"📅 {day_label} ({len(day_plans)} tasks)", expanded=(day == today)):
                for plan in day_plans:
                    subj = get_subject(plan["subject"])
                    done_icon = "✅" if plan["completed"] else "⭕"
                    priority_color = {"High": "🔴", "Normal": "🟡", "Low": "🟢"}.get(plan.get("priority","Normal"), "🟡")
                    st.markdown(
                        f"{done_icon} {subj['icon']} **{subj['name']}** — {plan['topic']} "
                        f"| {priority_color} {plan.get('priority','Normal')} "
                        f"| ⏱️ {plan['duration_minutes']} min"
                    )
        else:
            st.markdown(f"📅 {day_label} — *No tasks scheduled*")


def _render_study_tips():
    """Show study tips and recommendations."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 💡 Study Tips & Strategies")

    subject_names = ["🌟 General Tips"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
    subject_ids = [None] + [s["id"] for s in SUBJECTS]
    sel = st.selectbox("📚 Tips for:", subject_names, key="tips_subject")
    subject_id = subject_ids[subject_names.index(sel)]

    tips = get_study_tips(subject_id)

    for tip in tips:
        st.markdown(f"""
        <div class="tip-card">
            {tip}
        </div>
        """, unsafe_allow_html=True)

    # Study techniques
    st.markdown("---")
    st.markdown("### 🧠 Proven Study Techniques")

    techniques = {
        "⏱️ Pomodoro Technique": "Study for 25 minutes, then take a 5-minute break. After 4 cycles, take a 30-minute break. This keeps your brain fresh!",
        "✍️ Active Recall": "Instead of re-reading, close your book and try to write everything you remember. This is THE most powerful study technique!",
        "🔄 Spaced Repetition": "Review material after 1 day, then 3 days, then 1 week, then 2 weeks. This locks it into long-term memory!",
        "🗣️ The Feynman Technique": "Pretend you're teaching the concept to a younger student. If you can explain it simply, you truly understand it!",
        "🗺️ Mind Mapping": "Draw a diagram connecting ideas to a central topic. Great for history, science, and any subject with many connected facts!",
        "📊 Practice Tests": "Taking practice tests is more effective than re-reading notes. The AI quiz feature is perfect for this!",
    }

    for technique, explanation in techniques.items():
        with st.expander(technique):
            st.markdown(explanation)

    # Revision schedule
    st.markdown("---")
    st.markdown("### 📆 Suggested Revision Schedule")
    weak_areas = db.get_weak_areas()
    if weak_areas:
        st.warning("Based on your quiz scores, here's a focused revision schedule:")
        revision = get_revision_schedule(weak_areas)
        for session in revision:
            subj = get_subject(session["subject"])
            score = session.get("avg_score", 0)
            st.markdown(
                f"📅 **{session['date']}** — {subj['icon']} {subj['name']}: {session['topic']} "
                f"(Current avg: {score:.0f}%) | ⏱️ {session['duration_minutes']} min"
            )
    else:
        st.success("🌟 No specific revision needed! Keep up the regular study schedule.")
