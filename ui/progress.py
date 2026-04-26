"""
Progress Page UI - Student progress tracking and parent dashboard
"""

import streamlit as st
from utils.config import get_subject, get_subjects, BADGES
from utils.helpers import format_time, get_grade_emoji, get_score_color
import utils.database as db
from modules.adaptive_engine import (
    LEVEL_COLORS as ADAPTIVE_LEVEL_COLORS,
    ACTION_ICON as ADAPTIVE_ACTION_ICON,
)


def render_progress():
    """Render the progress tracking page."""
    st.markdown('<div class="page-title">📊 Progress Dashboard</div>', unsafe_allow_html=True)

    # Tabs for student view and parent view
    tab1, tab2, tab3 = st.tabs(["🎓 My Progress", "👨‍👩‍👧 Parent Dashboard", "🏅 My Badges"])

    with tab1:
        _render_student_progress()

    with tab2:
        _render_parent_dashboard()

    with tab3:
        _render_badges()


def _render_student_progress():
    """Student-friendly progress view."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    summary = db.get_dashboard_summary()
    student = summary["student"]
    name = student.get("name", "Student")

    # ── Top stats ────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, "⭐ Points",   summary["points"],                  None),
        (c2, "🔥 Streak",   f"{summary['streak']} days",        None),
        (c3, "📚 Chapters", summary["completed_chapters"],      None),
        (c4, "📝 Quizzes",  summary["quiz_count"],              None),
        (c5, "⏱️ Study",    format_time(summary["total_study_time"]), None),
    ]
    for col, label, value, delta in metrics:
        with col:
            st.metric(label, value, delta)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Subject Performance Chart ─────────────────────────────
    st.markdown("### 📊 Subject Performance")

    subj_stats = summary["subject_stats"]
    if subj_stats:
        for subj in SUBJECTS:
            sid = subj["id"]
            if sid in subj_stats:
                stat = subj_stats[sid]
                avg = stat.get("avg_score", 0)
                quizzes = stat.get("quiz_count", 0)
                color = get_score_color(avg)

                col1, col2, col3 = st.columns([2, 6, 2])
                with col1:
                    st.markdown(f"**{subj['icon']} {subj['name']}**")
                with col2:
                    st.progress(avg / 100, text=f"{avg:.0f}%")
                with col3:
                    st.markdown(f"*{quizzes} quiz(zes)*")
    else:
        st.info("📝 Complete some quizzes to see your performance here!")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Quiz History ───────────────────────────────────
    st.markdown("### 📋 Recent Quiz Results")
    quiz_history = db.get_quiz_history(limit=10)

    if quiz_history:
        for quiz in quiz_history:
            score = quiz["score_percent"]
            color = get_score_color(score)
            subj = get_subject(quiz["subject"])
            grade = get_grade_emoji(score)

            st.markdown(f"""
            <div class="quiz-history-item" style="border-left: 3px solid {color}">
                <span>{subj['icon']} <strong>{subj['name']}</strong></span>
                <span>📑 {quiz['chapter_title']}</span>
                <span style="color:{color}"><strong>{score:.0f}%</strong></span>
                <span>{grade.split()[0]}</span>
                <span>📅 {quiz['quiz_date']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No quizzes yet! Go to Practice to start! 🚀")

    # ── 🧠 Adaptive Levels by Chapter ─────────────────────────
    st.markdown("<br>")
    st.markdown("### 🧠 Your Adaptive Learning Levels")
    st.caption(
        "The tutor automatically adjusts difficulty per chapter based on your last quiz. "
        "Complete a quiz to see this update."
    )
    adaptive_rows = db.get_all_adaptive_profiles()
    if adaptive_rows:
        for row in adaptive_rows:
            subj = get_subject(row.get("subject") or "")
            level = row.get("current_level", "Medium")
            action = row.get("recommended_action", "Practice")
            acc = row.get("last_accuracy", 0) or 0
            attempts = row.get("attempts", 0) or 0
            level_color = ADAPTIVE_LEVEL_COLORS.get(level, "#74B9FF")
            action_icon = ADAPTIVE_ACTION_ICON.get(action, "📝")

            col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
            with col_a:
                st.markdown(
                    f"**{subj['icon']} {subj['name']}** — {row.get('chapter_title', '')}"
                )
            with col_b:
                st.markdown(
                    f"<span style='background:{level_color};color:white;"
                    f"padding:3px 10px;border-radius:999px;font-weight:700;'>"
                    f"🎯 {level}</span>",
                    unsafe_allow_html=True,
                )
            with col_c:
                st.markdown(f"{action_icon} **{action}**")
            with col_d:
                st.caption(f"Last: {acc:.0f}% • {attempts} attempt(s)")
    else:
        st.info("Take a quiz in any chapter to start building your adaptive profile! 🚀")

    # ── Weak Areas ────────────────────────────────────────────
    st.markdown("<br>")
    weak_areas = db.get_weak_areas()
    if weak_areas:
        st.markdown("### ⚠️ Topics to Revise")
        st.warning("These are areas where you scored below 60%. Let's improve them!")

        for area in weak_areas:
            subj = get_subject(area["subject"])
            attempts = area["attempts"]
            avg = area["avg_score"]

            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{subj['icon']} {subj['name']} — {area['chapter_title']}**")
            with col2:
                st.markdown(f"Avg Score: **{avg:.0f}%** ({attempts} attempt(s))")
            with col3:
                if st.button("📖 Revise Now", key=f"revise_{area['subject']}_{area['chapter_title'][:10]}"):
                    st.session_state.page = "learn"
                    st.session_state.selected_subject = area["subject"]
                    st.rerun()

    # ── Study Time Chart ──────────────────────────────────────
    st.markdown("<br>")
    st.markdown("### ⏱️ Study Time by Subject")
    study_time_by_subj = db.get_study_time_by_subject()

    if study_time_by_subj:
        for subj in SUBJECTS:
            sid = subj["id"]
            mins = study_time_by_subj.get(sid, 0)
            if mins > 0:
                col1, col2 = st.columns([2, 8])
                with col1:
                    st.markdown(f"{subj['icon']} **{subj['name']}**")
                with col2:
                    max_mins = max(study_time_by_subj.values()) if study_time_by_subj else 1
                    st.progress(mins / max_mins, text=format_time(mins))
    else:
        st.info("Study sessions will appear here after you start learning!")


def _render_parent_dashboard():
    """Clean parent-friendly summary dashboard."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 👨‍👩‍👧 Parent Summary Report")
    st.info("📋 A simple overview of your child's learning progress")

    summary = db.get_dashboard_summary()
    student = summary["student"]
    name = student.get("name", "Student")
    today_pts = db.get_points().get("today_points", 0)

    # ── Summary Cards ─────────────────────────────────────────
    st.markdown(f"#### 📊 {name}'s Learning Report")
    st.markdown(f"*Last updated: Today*")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="parent-card">
        """, unsafe_allow_html=True)

        st.markdown("**📈 Overall Stats**")
        stats_data = {
            "Total Points Earned": f"⭐ {summary['points']}",
            "Current Study Streak": f"🔥 {summary['streak']} days",
            "Total Study Days": f"📅 {summary['study_days']} days",
            "Total Study Time": f"⏱️ {format_time(summary['total_study_time'])}",
            "Chapters Completed": f"✅ {summary['completed_chapters']}",
            "Quizzes Taken": f"📝 {summary['quiz_count']}",
            "Badges Earned": f"🏅 {summary['badges_count']}",
            "Points Today": f"⭐ {today_pts}",
        }
        for key, val in stats_data.items():
            st.markdown(f"- **{key}:** {val}")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("**📊 Subject-wise Average Scores**")
        subj_stats = summary["subject_stats"]
        if subj_stats:
            for subj in SUBJECTS:
                sid = subj["id"]
                if sid in subj_stats:
                    stat = subj_stats[sid]
                    avg = stat.get("avg_score", 0)
                    grade_emoji = "✅" if avg >= 75 else ("⚠️" if avg >= 50 else "❌")
                    st.markdown(f"{grade_emoji} {subj['icon']} **{subj['name']}**: {avg:.0f}%")
        else:
            st.info("No quiz data yet. Encourage your child to take quizzes!")

    # ── Areas needing attention ───────────────────────────────
    st.markdown("<br>")
    weak_areas = summary["weak_areas"]
    if weak_areas:
        st.markdown("#### ⚠️ Topics Needing Extra Attention")
        st.warning("Your child scored below 60% in these topics. Consider extra practice or tuition help.")
        for area in weak_areas:
            subj = get_subject(area["subject"])
            st.markdown(f"• **{subj['name']} — {area['chapter_title']}**: {area['avg_score']:.0f}% average")
    else:
        if summary["quiz_count"] > 0:
            st.success("🌟 Excellent! No weak areas detected. Your child is performing well!")
        else:
            st.info("Complete some quizzes to see performance analysis.")

    # ── Recommendations ───────────────────────────────────────
    st.markdown("<br>")
    st.markdown("#### 💡 Recommendations for Parents")
    recommendations = _generate_parent_recommendations(summary)
    for rec in recommendations:
        st.markdown(f"• {rec}")


def _generate_parent_recommendations(summary):
    """Generate personalized recommendations for parents."""
    recs = []
    streak = summary["streak"]
    study_time = summary["total_study_time"]
    quiz_count = summary["quiz_count"]
    weak_areas = summary["weak_areas"]

    if streak == 0:
        recs.append("📅 **Encourage daily study habit** - even 30 minutes a day makes a big difference!")
    elif streak >= 7:
        recs.append("🔥 **Amazing streak!** Keep encouraging this daily habit - it's working!")

    if study_time < 60:
        recs.append("⏱️ **Increase study time** - Aim for at least 1-2 hours of focused study daily")

    if quiz_count < 5:
        recs.append("📝 **Encourage more practice** - Regular quizzes help reinforce learning")

    if weak_areas:
        subjects_weak = list(set([w["subject"] for w in weak_areas]))
        subj_names = [get_subject(s)["name"] for s in subjects_weak[:2]]
        recs.append(f"📚 **Extra practice needed in**: {', '.join(subj_names)}")

    if not recs:
        recs = [
            "✅ Your child is doing well! Keep up the encouragement.",
            "🎯 Try introducing new subjects to explore all areas of the syllabus",
            "🎮 The brain games section helps with cognitive development - encourage playing!"
        ]

    recs.append("💬 **Ask your child** to explain what they learned today - teaching reinforces memory!")
    recs.append("🌟 **Celebrate achievements** - praise effort, not just results!")
    return recs


def _render_badges():
    """Render earned badges and available badges."""
    st.markdown("### 🏅 Badge Collection")

    earned_badges = db.get_badges()
    earned_ids = {b["badge_id"] for b in earned_badges}

    if earned_badges:
        st.success(f"🎉 You have earned **{len(earned_badges)}** badge(s)! Keep going!")
        st.markdown("<br>", unsafe_allow_html=True)

        # Show earned badges
        st.markdown("#### ✅ Earned Badges")
        cols = st.columns(4)
        for i, badge in enumerate(earned_badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="badge-display earned">
                    <div class="badge-icon-large">{badge['badge_icon']}</div>
                    <div class="badge-name-display">{badge['badge_name']}</div>
                    <div class="badge-date">{badge['earned_date']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("You haven't earned any badges yet. Start learning to earn your first badge!")

    # Show locked badges
    st.markdown("<br>")
    st.markdown("#### 🔒 Badges to Earn")

    all_badges = BADGES
    locked = [b for b in all_badges if b["id"] not in earned_ids]

    if locked:
        cols = st.columns(4)
        for i, badge in enumerate(locked):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="badge-display locked">
                    <div class="badge-icon-large" style="filter:grayscale(1);opacity:0.5">🔒</div>
                    <div class="badge-name-display" style="color:#999">{badge['name']}</div>
                    <div class="badge-date" style="color:#aaa">{badge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("🎉 You've earned ALL badges! You're a champion!")

    # Points summary
    st.markdown("<br>")
    points = db.get_total_points()
    level = _get_level(points)

    st.markdown(f"""
    <div class="level-display">
        <div class="level-icon">{level['icon']}</div>
        <div class="level-info">
            <div class="level-name">{level['name']}</div>
            <div class="level-points">{points} points</div>
            <div class="level-next">Next level: {level['next_level']} ({level['points_needed']} more points)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _get_level(points):
    levels = [
        (0,    "🌱 Seedling",     "🌿 Explorer",   100),
        (100,  "🌿 Explorer",     "⭐ Learner",     300),
        (300,  "⭐ Learner",      "📚 Scholar",     700),
        (700,  "📚 Scholar",      "🔥 Achiever",    1500),
        (1500, "🔥 Achiever",     "💫 Champion",    3000),
        (3000, "💫 Champion",     "🏆 Master",      5000),
        (5000, "🏆 Master",       "🌟 Genius",      10000),
        (10000,"🌟 Genius",       "👑 Legend",      99999),
    ]
    current = levels[0]
    for threshold, name, next_name, needed in levels:
        if points >= threshold:
            current = (threshold, name, next_name, needed)
    _, name, next_level, points_for_next = current
    pts_needed = max(0, points_for_next - points)
    icon = name.split()[0]
    return {"name": name, "icon": icon, "next_level": next_level, "points_needed": pts_needed}
