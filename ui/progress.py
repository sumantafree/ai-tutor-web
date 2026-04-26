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
from modules.ai_engine import generate_parent_recommendations, is_valid_gemini_key


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
    """Phase 3: comprehensive parent-facing dashboard."""
    import os as _os
    from datetime import date as _date
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    summary = db.get_dashboard_summary()
    student = summary["student"]
    name = student.get("name", "Student")
    avatar = student.get("avatar", "🎓")

    week = db.get_week_summary(days=7)
    cmp = db.get_week_comparison(days=7)

    # ── Header card ───────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg,#1a1a2e,#16213e);
                    color:white; border-radius:16px; padding:1.2rem 1.5rem;
                    margin-bottom:1rem;">
            <div style="font-size:1.05rem; opacity:0.8;">📋 Weekly Learning Report</div>
            <div style="font-size:1.6rem; font-weight:800; margin-top:0.2rem;">
                {avatar}  {name}'s Week
            </div>
            <div style="opacity:0.7; font-size:0.95rem; margin-top:0.2rem;">
                Last 7 days · Updated {_date.today().strftime('%A, %d %B %Y')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── This Week At A Glance ─────────────────────────────────
    st.markdown("#### 📊 This Week At A Glance")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_min = week["study_minutes"] - cmp["last_minutes"]
        st.metric("⏱️ Study time",
                  format_time(week["study_minutes"]),
                  f"{'+' if delta_min >= 0 else ''}{delta_min} min vs last week",
                  delta_color="normal" if delta_min >= 0 else "inverse")
    with c2:
        delta_q = week["quizzes_taken"] - cmp["last_quizzes"]
        st.metric("📝 Quizzes",
                  week["quizzes_taken"],
                  f"{'+' if delta_q >= 0 else ''}{delta_q} vs last week",
                  delta_color="normal" if delta_q >= 0 else "inverse")
    with c3:
        delta_s = round(week["avg_score"] - cmp["last_avg_score"], 1)
        st.metric("🎯 Avg score",
                  f"{week['avg_score']:.0f}%" if week["avg_score"] else "—",
                  f"{'+' if delta_s >= 0 else ''}{delta_s}% vs last week"
                  if cmp["last_avg_score"] > 0 else None,
                  delta_color="normal" if delta_s >= 0 else "inverse")
    with c4:
        st.metric("📸 Doubts solved", week["doubts_solved"])
    st.caption(f"Active on **{week['active_days']} of 7 days**.")

    # ── Daily activity chart ──────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📅 Daily Activity")
    minutes_by_day = week["study_minutes_by_day"]
    quizzes_by_day = week["quizzes_by_day"]
    if any(minutes_by_day.values()) or any(quizzes_by_day.values()):
        # Build a tiny dict-of-lists structure that st.bar_chart understands
        chart_data = {
            "Study minutes": list(minutes_by_day.values()),
            "Quizzes taken": list(quizzes_by_day.values()),
        }
        # Use the date short labels as the x-axis index
        day_labels = [_short_day_label(d) for d in minutes_by_day.keys()]
        try:
            import pandas as _pd
            df = _pd.DataFrame(chart_data, index=day_labels)
            st.bar_chart(df, use_container_width=True)
        except Exception:
            # Fallback without pandas
            for d, m in minutes_by_day.items():
                qc = quizzes_by_day.get(d, 0)
                st.markdown(f"- **{_short_day_label(d)}** — {m} min · {qc} quiz")
    else:
        st.info("No activity in the last 7 days yet.")

    # ── Subject performance ──────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📚 Subject Performance (all-time)")
    subj_stats = summary["subject_stats"]
    if subj_stats:
        ranked = sorted(
            [(s, subj_stats[s["id"]]) for s in SUBJECTS if s["id"] in subj_stats],
            key=lambda t: t[1].get("avg_score", 0) or 0,
            reverse=True,
        )
        strongest_subject_name = ranked[0][0]["name"] if ranked else None
        for subj, stat in ranked:
            avg = stat.get("avg_score", 0) or 0
            qcount = stat.get("quiz_count", 0) or 0
            color = get_score_color(avg)
            col_a, col_b, col_c = st.columns([2, 6, 2])
            with col_a:
                st.markdown(f"**{subj['icon']} {subj['name']}**")
            with col_b:
                st.progress(min(max(avg / 100.0, 0.0), 1.0),
                            text=f"{avg:.0f}% avg over {qcount} quiz(zes)")
            with col_c:
                if avg >= 75:
                    st.markdown("✅ Strong")
                elif avg >= 50:
                    st.markdown("🟡 OK")
                else:
                    st.markdown("🔴 Weak")
    else:
        strongest_subject_name = None
        st.info("No quiz data yet. Encourage your child to take a quiz today.")

    # ── Topics that need attention ───────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ⚠️ Topics That Need Attention")
    weak_areas = summary["weak_areas"] or []
    if weak_areas:
        for area in weak_areas[:5]:
            subj = get_subject(area["subject"])
            avg = area.get("avg_score", 0) or 0
            attempts = area.get("attempts", 0) or 0
            ca, cb = st.columns([5, 1])
            with ca:
                st.markdown(
                    f"**{subj['icon']} {subj['name']} — {area['chapter_title']}**  "
                    f"<span style='color:#636e72;'>· avg {avg:.0f}% over {attempts} attempt(s)</span>",
                    unsafe_allow_html=True,
                )
            with cb:
                if st.button("📖 Revise", key=f"parent_revise_{area['subject']}_{area['chapter_title'][:14]}"):
                    st.session_state.page = "learn"
                    st.session_state.selected_subject = area["subject"]
                    st.rerun()
    else:
        st.success("🌟 No weak topics right now — your child is on track!")

    # ── AI recommendations ──────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Personalized Recommendations")

    # Build the small payload for the AI
    ai_payload = {
        "student_name": name,
        "week": {
            "study_minutes": week["study_minutes"],
            "quizzes_taken": week["quizzes_taken"],
            "avg_score": week["avg_score"],
            "doubts_solved": week["doubts_solved"],
            "active_days": week["active_days"],
        },
        "previous_week": {
            "study_minutes": cmp["last_minutes"],
            "quizzes_taken": cmp["last_quizzes"],
            "avg_score": cmp["last_avg_score"],
        },
        "weak_areas": [
            {
                "subject": get_subject(w["subject"])["name"],
                "chapter_title": w["chapter_title"],
                "avg_score": round(float(w.get("avg_score") or 0), 1),
                "attempts": w.get("attempts", 0),
            }
            for w in weak_areas[:5]
        ],
        "strongest_subject": strongest_subject_name,
        "completed_chapters": summary.get("completed_chapters", 0),
        "current_streak_days": summary.get("streak", 0),
    }

    api_key = student.get("api_key", "") or ""
    has_ai = is_valid_gemini_key(api_key) or is_valid_gemini_key(_os.environ.get("GEMINI_API_KEY", ""))

    cache_key = f"_parent_recs_v1_{name}_{week['quizzes_taken']}_{week['doubts_solved']}_{week['study_minutes']}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = None

    if st.session_state[cache_key] is None:
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("✨ Generate", key="gen_parent_recs",
                         use_container_width=True, type="primary"):
                with st.spinner("Thinking…"):
                    text, used_ai = generate_parent_recommendations(ai_payload, api_key=api_key)
                st.session_state[cache_key] = {"text": text, "used_ai": used_ai}
                st.rerun()
        with col_b:
            st.caption(
                "Click **Generate** to get a personalised, AI-written summary of "
                f"what to focus on this week. {'✅ Gemini connected.' if has_ai else '🟡 Add your Gemini API key in ⚙️ Settings for AI-powered advice (basic version still works without it).'}"
            )
    else:
        rec = st.session_state[cache_key]
        st.markdown(rec["text"])
        st.caption("✅ AI-generated" if rec["used_ai"] else "ℹ️ Built-in (basic) — add a Gemini API key for richer advice.")
        if st.button("🔄 Regenerate", key="regen_parent_recs"):
            st.session_state[cache_key] = None
            st.rerun()

    # ── Recent activity log ─────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🕒 Recent Activity")
    events = db.get_recent_activity_log(limit=15)
    if events:
        for e in events[:12]:
            ts = (e.get("ts") or "")[:16].replace("T", " ")
            subject = e.get("subject") or ""
            subj_label = ""
            if subject:
                try:
                    s = get_subject(subject)
                    subj_label = f"{s['icon']} {s['name']}"
                except Exception:
                    subj_label = subject
            detail = e.get("detail") or ""
            st.markdown(
                f"- 🕒 `{ts}`  ·  {subj_label}  ·  {e['label']}"
                + (f"  <span style='color:#636e72;'>· {detail}</span>" if detail else ""),
                unsafe_allow_html=True,
            )
    else:
        st.info("No activity logged yet.")

    # ── Footer: overall stats ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏆 All-time totals")
    today_pts = db.get_points().get("today_points", 0)
    cols = st.columns(4)
    with cols[0]: st.metric("⭐ Points",   summary["points"])
    with cols[1]: st.metric("🔥 Streak",   f"{summary['streak']} days")
    with cols[2]: st.metric("📚 Chapters", summary["completed_chapters"])
    with cols[3]: st.metric("🏅 Badges",   summary["badges_count"])


def _short_day_label(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to 'Mon 24' style label for charts."""
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(date_str, "%Y-%m-%d").date()
        return d.strftime("%a %d")
    except Exception:
        return date_str


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
