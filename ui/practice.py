"""
Practice Page UI - Quizzes, tests, and question answering
"""

import streamlit as st
import time
import html as html_module
from utils.config import SUBJECTS, SYLLABUS, get_subject, DIFFICULTY_LEVELS
from utils.helpers import get_grade_emoji, get_score_color, get_difficulty_color
import utils.database as db
from modules.quiz_engine import build_quiz, score_quiz, build_practice_test, get_rapid_fire_questions


def render_practice():
    """Render the practice/quiz page."""

    st.markdown('<div class="page-title">📝 Practice & Quizzes</div>', unsafe_allow_html=True)

    # ── Quiz Mode Tabs ───────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Chapter Quiz", "📋 Practice Test", "⚡ Rapid Fire", "📖 Homework Solver"
    ])

    with tab1:
        _render_chapter_quiz()

    with tab2:
        _render_practice_test()

    with tab3:
        _render_rapid_fire()

    with tab4:
        _render_homework_solver()


# ─────────────────────────────────────────────────────────
# CHAPTER QUIZ
# ─────────────────────────────────────────────────────────

def _render_chapter_quiz():
    """Chapter-specific quiz."""

    student = db.get_student()
    api_key = student.get("api_key", "") or ""

    # Setup form
    if not st.session_state.get("quiz_active"):
        col1, col2, col3 = st.columns(3)

        with col1:
            subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
            subject_ids = [s["id"] for s in SUBJECTS]

            default_idx = 0
            if st.session_state.get("practice_subject"):
                sid = st.session_state.practice_subject
                if sid in subject_ids:
                    default_idx = subject_ids.index(sid)

            sel_name = st.selectbox("📚 Subject", subject_names, index=default_idx, key="quiz_subject")
            subject_id = subject_ids[subject_names.index(sel_name)]

        with col2:
            subj_data = SYLLABUS.get(subject_id, {})
            chapters = subj_data.get("chapters", [])
            chapter_titles = [ch["title"] for ch in chapters] if chapters else ["General"]

            default_ch = 0
            pchap = st.session_state.get("practice_chapter", "")
            if pchap and pchap in chapter_titles:
                default_ch = chapter_titles.index(pchap)

            selected_chapter = st.selectbox("📑 Chapter", chapter_titles, index=default_ch, key="quiz_chapter")

        with col3:
            difficulty = st.selectbox("🎯 Difficulty", DIFFICULTY_LEVELS, index=1, key="quiz_diff")

        num_q = st.slider("Number of Questions", 3, 10, 5, key="quiz_num_q")

        # Check for uploaded content
        uploaded = db.get_uploaded_content(subject_id)
        uploaded_text = ""
        if uploaded:
            uploaded_text = " ".join([u.get("extracted_text", "") for u in uploaded[:2]])
            st.success(f"✅ {len(uploaded)} uploaded file(s) found - questions will include content from your books!")

        if st.button("🚀 Start Quiz!", key="start_quiz", use_container_width=True):
            with st.spinner("Generating questions..."):
                questions = build_quiz(
                    subject=subject_id,
                    chapter_title=selected_chapter,
                    difficulty=difficulty,
                    count=num_q,
                    api_key=api_key,
                    uploaded_text=uploaded_text
                )
            st.session_state.quiz_active = True
            st.session_state.quiz_questions = questions
            st.session_state.quiz_answers = [""] * len(questions)
            st.session_state.quiz_subject = subject_id
            st.session_state.quiz_chapter = selected_chapter
            st.session_state.quiz_difficulty = difficulty
            st.session_state.quiz_start_time = time.time()
            st.session_state.quiz_submitted = False
            st.rerun()
    else:
        _run_quiz()


def _run_quiz():
    """Run an active quiz session."""
    questions = st.session_state.get("quiz_questions", [])
    subject_id = st.session_state.get("quiz_subject", "")
    chapter = st.session_state.get("quiz_chapter", "")
    difficulty = st.session_state.get("quiz_difficulty", "Medium")
    subj = get_subject(subject_id)
    submitted = st.session_state.get("quiz_submitted", False)

    if not questions:
        st.error("No questions loaded. Please go back and try again.")
        if st.button("← Back"):
            st.session_state.quiz_active = False
            st.rerun()
        return

    # Quiz header
    elapsed = int(time.time() - st.session_state.get("quiz_start_time", time.time()))
    mins, secs = divmod(elapsed, 60)
    diff_color = get_difficulty_color(difficulty)

    st.markdown(f"""
    <div class="quiz-header" style="border-left: 4px solid {subj['color']}">
        <span>{subj['icon']} {subj['name']}</span> |
        <span>📑 {chapter}</span> |
        <span style="color:{diff_color}">🎯 {difficulty}</span> |
        <span>⏱️ {mins:02d}:{secs:02d}</span> |
        <span>📊 {len(questions)} Questions</span>
    </div>
    """, unsafe_allow_html=True)

    if not submitted:
        # Show questions
        answers = list(st.session_state.quiz_answers)

        for i, q in enumerate(questions):
            q_type = q.get("type", "short")
            options = q.get("options", [])

            st.markdown(f"""
            <div class="question-card">
                <div class="question-number">Question {i+1} of {len(questions)}</div>
                <div class="question-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            if q_type == "mcq" and options:
                ans = st.radio(
                    f"Choose your answer:", options,
                    key=f"q_mcq_{i}", label_visibility="collapsed"
                )
                answers[i] = ans if ans else ""
            else:
                ans = st.text_input(
                    "Your answer:", key=f"q_text_{i}",
                    value=answers[i], placeholder="Type your answer here..."
                )
                answers[i] = ans

            st.markdown("<hr style='margin:8px 0;border-color:#eee'>", unsafe_allow_html=True)

        st.session_state.quiz_answers = answers

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit Quiz", key="submit_quiz", use_container_width=True):
                # Set answers in questions
                for i, q in enumerate(questions):
                    q["student_answer"] = answers[i]
                st.session_state.quiz_questions = questions
                st.session_state.quiz_submitted = True
                st.session_state.quiz_time_taken = int(time.time() - st.session_state.quiz_start_time)
                st.rerun()
        with col2:
            if st.button("❌ Cancel Quiz", key="cancel_quiz", use_container_width=True):
                st.session_state.quiz_active = False
                st.session_state.quiz_submitted = False
                st.rerun()
    else:
        # Show results
        _show_quiz_results(questions, subject_id, chapter, difficulty)


def _show_quiz_results(questions, subject_id, chapter, difficulty):
    """Show quiz results with detailed feedback."""
    correct, total, percentage, results = score_quiz(questions)
    time_taken = st.session_state.get("quiz_time_taken", 0)

    # Save to database
    db.save_quiz_result(subject_id, chapter, difficulty, total, correct, time_taken)

    # Save individual answers
    for r in results:
        db.save_question_attempt(
            subject_id, chapter,
            r["question"], r["student_answer"],
            r["correct_answer"], r["is_correct"], difficulty
        )

    # Check badges
    from utils.helpers import check_and_award_badges
    new_badges = check_and_award_badges(db)
    if new_badges:
        for badge in new_badges:
            st.balloons()
            st.success(f"🎉 New Badge Earned: {badge['badge_icon']} **{badge['badge_name']}**!")

    # Results header
    score_color = get_score_color(percentage)
    grade_msg = get_grade_emoji(percentage)

    st.markdown(f"""
    <div class="results-banner" style="background: linear-gradient(135deg, {score_color}22, {score_color}44); border: 2px solid {score_color}">
        <div class="results-score" style="color: {score_color}">{percentage:.0f}%</div>
        <div class="results-grade">{grade_msg}</div>
        <div class="results-detail">✅ {correct} / {total} correct | ⏱️ {time_taken//60:02d}:{time_taken%60:02d}</div>
    </div>
    """, unsafe_allow_html=True)

    # Points awarded
    pts = correct * 10
    st.success(f"⭐ You earned **{pts} points**!")

    # Detailed results
    st.markdown("### 📊 Detailed Results")
    for i, r in enumerate(results):
        icon = "✅" if r["is_correct"] else "❌"
        with st.expander(f"{icon} Q{i+1}: {r['question'][:60]}..."):
            if r["is_correct"]:
                st.success(f"Your answer: **{r['student_answer']}** ✅")
            else:
                st.error(f"Your answer: **{r['student_answer']}** ❌")
                st.success(f"Correct answer: **{r['correct_answer']}**")

    st.markdown("<br>")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Try Again", key="retry_quiz", use_container_width=True):
            st.session_state.quiz_active = False
            st.session_state.quiz_submitted = False
            st.rerun()
    with col2:
        if st.button("📖 Review Chapter", key="review_chapter", use_container_width=True):
            st.session_state.page = "learn"
            st.session_state.selected_subject = subject_id
            st.session_state.quiz_active = False
            st.rerun()
    with col3:
        if st.button("🏠 Home", key="quiz_home", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.quiz_active = False
            st.rerun()


# ─────────────────────────────────────────────────────────
# FULL PRACTICE TEST
# ─────────────────────────────────────────────────────────

def _render_practice_test():
    """Full subject practice test."""
    student = db.get_student()
    api_key = student.get("api_key", "") or ""

    if not st.session_state.get("test_active"):
        st.markdown("### 📋 Full Subject Practice Test")
        st.info("This test covers ALL chapters of a subject — great exam preparation!")

        col1, col2 = st.columns(2)
        with col1:
            subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
            subject_ids = [s["id"] for s in SUBJECTS]
            sel = st.selectbox("📚 Subject", subject_names, key="test_subject")
            subject_id = subject_ids[subject_names.index(sel)]

        with col2:
            difficulty = st.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard", "Mixed"], index=3, key="test_diff")

        num_q = st.slider("Number of Questions", 5, 20, 10, key="test_num_q")

        if st.button("📋 Start Practice Test", use_container_width=True, key="start_test"):
            with st.spinner("Building your practice test..."):
                questions = build_practice_test(subject_id, difficulty, num_q, api_key)
            st.session_state.test_active = True
            st.session_state.test_questions = questions
            st.session_state.test_answers = [""] * len(questions)
            st.session_state.test_subject = subject_id
            st.session_state.test_difficulty = difficulty
            st.session_state.test_start_time = time.time()
            st.rerun()
    else:
        _run_test_session()


def _run_test_session():
    """Run the full practice test."""
    questions = st.session_state.get("test_questions", [])
    subject_id = st.session_state.get("test_subject", "")
    subj = get_subject(subject_id)

    if not questions:
        st.error("No questions. Please restart.")
        st.session_state.test_active = False
        return

    st.markdown(f"### {subj['icon']} Practice Test: {subj['name']}")
    st.markdown(f"**{len(questions)} Questions** | Answer all and submit when ready.")

    answers = list(st.session_state.test_answers)

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}.** {q['question']}")
        ans = st.text_input(f"Answer {i+1}:", key=f"test_ans_{i}", value=answers[i])
        answers[i] = ans
        st.markdown("---")

    st.session_state.test_answers = answers

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Test", key="submit_test", use_container_width=True):
            for i, q in enumerate(questions):
                q["student_answer"] = answers[i]
            st.session_state.test_questions = questions

            correct, total, pct, results = score_quiz(questions)
            time_taken = int(time.time() - st.session_state.test_start_time)
            diff = st.session_state.get("test_difficulty", "Mixed")
            db.save_quiz_result(subject_id, "Full Practice Test", diff, total, correct, time_taken)

            st.success(f"🎉 Test Complete! Score: **{pct:.0f}%** ({correct}/{total}) | {get_grade_emoji(pct)}")
            st.info(f"⭐ +{correct*10} points earned!")
            st.session_state.test_active = False
    with col2:
        if st.button("❌ Cancel Test", key="cancel_test", use_container_width=True):
            st.session_state.test_active = False
            st.rerun()


# ─────────────────────────────────────────────────────────
# RAPID FIRE
# ─────────────────────────────────────────────────────────

def _render_rapid_fire():
    """Rapid fire question mode - 10 questions, limited time."""

    st.markdown("### ⚡ Rapid Fire Quiz")
    st.info("Answer questions as fast as you can! 10 questions | Try to beat your best score!")

    if not st.session_state.get("rapid_active"):
        subject_names = ["🌟 All Subjects"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = [None] + [s["id"] for s in SUBJECTS]

        sel = st.selectbox("📚 Subject", subject_names, key="rapid_subject")
        subject_id = subject_ids[subject_names.index(sel)]

        if st.button("⚡ Start Rapid Fire!", use_container_width=True, key="start_rapid"):
            questions = get_rapid_fire_questions(subject_id, 10)
            if not questions:
                questions = get_rapid_fire_questions(None, 10)
            st.session_state.rapid_active = True
            st.session_state.rapid_questions = questions
            st.session_state.rapid_idx = 0
            st.session_state.rapid_correct = 0
            st.session_state.rapid_start = time.time()
            st.session_state.rapid_answered = []
            st.rerun()
    else:
        _run_rapid_fire()


def _run_rapid_fire():
    """Run rapid fire question by question."""
    questions = st.session_state.get("rapid_questions", [])
    idx = st.session_state.get("rapid_idx", 0)
    correct_count = st.session_state.get("rapid_correct", 0)

    if idx >= len(questions) or idx >= 10:
        # Show score
        total_time = int(time.time() - st.session_state.rapid_start)
        pct = (correct_count / 10) * 100
        st.markdown(f"""
        <div class="rapid-results">
            <div style="font-size:3rem">⚡</div>
            <div style="font-size:2.5rem; font-weight:bold; color:#FDCB6E">{correct_count}/10</div>
            <div style="font-size:1.5rem">{get_grade_emoji(pct)}</div>
            <div>Time: {total_time} seconds</div>
        </div>
        """, unsafe_allow_html=True)

        db.save_game_score("Rapid Fire", correct_count * 10, "Medium")
        if st.button("⚡ Play Again", use_container_width=True, key="rapid_again"):
            st.session_state.rapid_active = False
            st.rerun()
        return

    q = questions[idx]
    elapsed = int(time.time() - st.session_state.rapid_start)

    # Progress
    progress = idx / 10
    st.progress(progress, text=f"Question {idx+1}/10 | ✅ {correct_count} correct | ⏱️ {elapsed}s")

    st.markdown(f"""
    <div class="rapid-question">
        <div class="rapid-num">⚡ Q{idx+1}</div>
        <div class="rapid-q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    answer = st.text_input("Your answer:", key=f"rapid_ans_{idx}", placeholder="Type fast!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Next", key=f"rapid_next_{idx}", use_container_width=True):
            from modules.quiz_engine import _check_answer
            is_correct = _check_answer(answer.strip().lower(), q["answer"].strip().lower())
            if is_correct:
                st.session_state.rapid_correct += 1
            st.session_state.rapid_answered.append({
                "q": q["question"], "your": answer, "correct": q["answer"], "ok": is_correct
            })
            st.session_state.rapid_idx += 1
            st.rerun()
    with col2:
        if st.button("🏳️ Stop", key=f"rapid_stop_{idx}", use_container_width=True):
            st.session_state.rapid_idx = 10  # End the quiz
            st.rerun()


# ─────────────────────────────────────────────────────────
# HOMEWORK SOLVER
# ─────────────────────────────────────────────────────────

def _render_homework_solver():
    """AI-powered homework solver."""
    st.markdown("### 📖 Homework Solver")
    st.info("📝 Type your homework question and get a step-by-step explanation!")

    student = db.get_student()
    api_key = student.get("api_key", "") or ""

    subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
    subject_ids = [s["id"] for s in SUBJECTS]

    col1, col2 = st.columns([1, 3])
    with col1:
        sel = st.selectbox("📚 Subject", subject_names, key="hw_subject")
        subject_id = subject_ids[subject_names.index(sel)]

    with col2:
        problem = st.text_area(
            "📝 Paste your homework question here:",
            height=120,
            placeholder="E.g., 'Solve: 3x + 7 = 22' or 'Explain photosynthesis' or 'Write a note on the Mauryan Empire'",
            key="hw_problem"
        )

    if st.button("🔍 Solve Step by Step", key="hw_solve", use_container_width=True):
        if not problem.strip():
            st.warning("Please enter a question first!")
        else:
            with st.spinner("🤖 Solving your problem step by step..."):
                from modules.ai_engine import solve_homework
                solution = solve_homework(problem, get_subject(subject_id)["name"], api_key)

            st.markdown("### 💡 Solution:")
            st.markdown(f"""
            <div class="solution-box">
                {html_module.escape(solution)}
            </div>
            """, unsafe_allow_html=True)

            db.add_points(5)
            st.success("⭐ +5 points for seeking help!")
