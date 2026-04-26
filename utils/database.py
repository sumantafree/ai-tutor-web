"""
Database layer - SQLite (local) / Postgres via Supabase (cloud)
Set DATABASE_URL env var to a Postgres connection string for cloud mode.
Otherwise falls back to local SQLite at DB_PATH.
"""

import os
import sqlite3
from datetime import date, timedelta
from utils.config import DB_PATH, DATA_DIR

DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
USE_PG = DATABASE_URL.startswith(("postgres://", "postgresql://"))

if USE_PG:
    import psycopg2
    import psycopg2.extras


# ─────────────────────────────────────────────────────────
# CONNECTION / CURSOR HELPERS
# ─────────────────────────────────────────────────────────

def get_connection():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _cursor(conn):
    if USE_PG:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn.cursor()


def _q(sql: str) -> str:
    """Translate ? placeholders to %s for Postgres."""
    return sql.replace("?", "%s") if USE_PG else sql


def _exec(conn, sql, params=()):
    cur = _cursor(conn)
    cur.execute(_q(sql), params)
    return cur


def _row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


def _fetchone(conn, sql, params=()):
    return _row_to_dict(_exec(conn, sql, params).fetchone())


def _fetchall(conn, sql, params=()):
    return [_row_to_dict(r) for r in _exec(conn, sql, params).fetchall()]


# ─────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────────────────

def _ddl():
    """Return list of DDL statements for the active backend."""
    if USE_PG:
        pk_auto = "SERIAL PRIMARY KEY"
        ts_default = "TIMESTAMP DEFAULT NOW()"
    else:
        pk_auto = "INTEGER PRIMARY KEY AUTOINCREMENT"
        ts_default = "TEXT DEFAULT CURRENT_TIMESTAMP"

    return [
        f"""CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY,
            name TEXT DEFAULT 'Student',
            age INTEGER DEFAULT 11,
            class_name TEXT DEFAULT 'Class 6',
            board TEXT DEFAULT 'ICSE',
            api_key TEXT DEFAULT '',
            avatar TEXT DEFAULT '🎓',
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS study_sessions (
            id {pk_auto},
            subject TEXT,
            chapter_id INTEGER,
            chapter_title TEXT,
            duration_minutes INTEGER DEFAULT 0,
            session_date TEXT DEFAULT '',
            activity_type TEXT DEFAULT 'learn',
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS quiz_results (
            id {pk_auto},
            subject TEXT,
            chapter_title TEXT,
            difficulty TEXT,
            total_questions INTEGER,
            correct_answers INTEGER,
            score_percent REAL,
            time_taken_seconds INTEGER DEFAULT 0,
            quiz_date TEXT DEFAULT '',
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS question_history (
            id {pk_auto},
            subject TEXT,
            chapter_title TEXT,
            question TEXT,
            student_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'Medium',
            attempt_date TEXT DEFAULT ''
        )""",
        f"""CREATE TABLE IF NOT EXISTS badges (
            id {pk_auto},
            badge_id TEXT UNIQUE,
            badge_name TEXT,
            badge_icon TEXT,
            earned_date TEXT DEFAULT ''
        )""",
        """CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY,
            total_points INTEGER DEFAULT 0,
            today_points INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT ''
        )""",
        f"""CREATE TABLE IF NOT EXISTS streaks (
            id {pk_auto},
            study_date TEXT UNIQUE,
            studied INTEGER DEFAULT 1
        )""",
        f"""CREATE TABLE IF NOT EXISTS chat_history (
            id {pk_auto},
            role TEXT,
            message TEXT,
            subject TEXT DEFAULT 'general',
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS uploaded_content (
            id {pk_auto},
            filename TEXT,
            subject TEXT,
            content_type TEXT,
            extracted_text TEXT,
            file_path TEXT,
            upload_date TEXT DEFAULT '',
            processed INTEGER DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS study_plan (
            id {pk_auto},
            plan_date TEXT,
            subject TEXT,
            topic TEXT,
            duration_minutes INTEGER DEFAULT 30,
            completed INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Normal'
        )""",
        f"""CREATE TABLE IF NOT EXISTS game_scores (
            id {pk_auto},
            game_name TEXT,
            score INTEGER,
            level TEXT,
            play_date TEXT DEFAULT ''
        )""",
        f"""CREATE TABLE IF NOT EXISTS chapter_progress (
            id {pk_auto},
            subject TEXT,
            chapter_id INTEGER,
            chapter_title TEXT,
            completed INTEGER DEFAULT 0,
            completion_date TEXT,
            UNIQUE(subject, chapter_id)
        )""",
        f"""CREATE TABLE IF NOT EXISTS doubt_history (
            id {pk_auto},
            subject TEXT,
            note TEXT,
            ai_response TEXT,
            image_filename TEXT,
            image_size_kb INTEGER DEFAULT 0,
            doubt_date TEXT DEFAULT '',
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS adaptive_profile (
            id {pk_auto},
            subject TEXT NOT NULL,
            chapter_title TEXT NOT NULL,
            current_level TEXT DEFAULT 'Medium',
            last_accuracy REAL DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            recommended_action TEXT DEFAULT 'Practice',
            updated_at {ts_default},
            UNIQUE(subject, chapter_title)
        )""",
        # ───── Dynamic Curriculum (Phase 4) ─────
        f"""CREATE TABLE IF NOT EXISTS cur_subjects (
            id {pk_auto},
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            icon TEXT DEFAULT '📚',
            color TEXT DEFAULT '#74B9FF',
            bg TEXT DEFAULT '#E5F4FB',
            sort_order INTEGER DEFAULT 0,
            created_at {ts_default}
        )""",
        f"""CREATE TABLE IF NOT EXISTS cur_chapters (
            id {pk_auto},
            subject_id INTEGER NOT NULL,
            original_id INTEGER DEFAULT 0,
            title TEXT NOT NULL,
            explanation TEXT DEFAULT '',
            topics_json TEXT DEFAULT '[]',
            key_points_json TEXT DEFAULT '[]',
            examples_json TEXT DEFAULT '[]',
            questions_json TEXT DEFAULT '[]',
            sort_order INTEGER DEFAULT 0,
            created_at {ts_default}
        )""",
    ]


def init_database():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    for stmt in _ddl():
        _exec(conn, stmt)

    # Seed default rows
    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM student")
    if (row.get("c") if row else 0) == 0:
        _exec(conn, "INSERT INTO student (id, name) VALUES (1, 'Student')")

    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM points")
    if (row.get("c") if row else 0) == 0:
        _exec(conn, "INSERT INTO points (id, total_points) VALUES (1, 0)")

    conn.commit()
    conn.close()
    print(f"Database initialized ({'Postgres' if USE_PG else 'SQLite'})")


# ─────────────────────────────────────────────────────────
# STUDENT
# ─────────────────────────────────────────────────────────

def get_student():
    conn = get_connection()
    student = _fetchone(conn, "SELECT * FROM student LIMIT 1") or {}
    conn.close()
    return student


def update_student(name=None, age=None, api_key=None, avatar=None):
    conn = get_connection()
    if name is not None:
        _exec(conn, "UPDATE student SET name=? WHERE id=1", (name,))
    if age is not None:
        _exec(conn, "UPDATE student SET age=? WHERE id=1", (age,))
    if api_key is not None:
        _exec(conn, "UPDATE student SET api_key=? WHERE id=1", (api_key,))
    if avatar is not None:
        _exec(conn, "UPDATE student SET avatar=? WHERE id=1", (avatar,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# POINTS
# ─────────────────────────────────────────────────────────

def get_points():
    conn = get_connection()
    row = _fetchone(conn, "SELECT * FROM points WHERE id=1")
    conn.close()
    return row or {"total_points": 0, "today_points": 0}


def add_points(amount, reason=""):
    conn = get_connection()
    today = str(date.today())
    row = _fetchone(conn, "SELECT * FROM points WHERE id=1")
    if row:
        last_updated = row.get("last_updated") or ""
        today_pts = row.get("today_points", 0) if last_updated == today else 0
        _exec(
            conn,
            "UPDATE points SET total_points=total_points+?, today_points=?, last_updated=? WHERE id=1",
            (amount, today_pts + amount, today),
        )
    conn.commit()
    conn.close()
    record_streak()


def get_total_points():
    return get_points().get("total_points", 0) or 0


# ─────────────────────────────────────────────────────────
# STREAKS
# ─────────────────────────────────────────────────────────

def record_streak():
    today = str(date.today())
    conn = get_connection()
    if USE_PG:
        _exec(conn, "INSERT INTO streaks (study_date) VALUES (?) ON CONFLICT (study_date) DO NOTHING", (today,))
    else:
        _exec(conn, "INSERT OR IGNORE INTO streaks (study_date) VALUES (?)", (today,))
    conn.commit()
    conn.close()


def get_current_streak():
    conn = get_connection()
    rows = _fetchall(conn, "SELECT study_date FROM streaks ORDER BY study_date DESC")
    conn.close()
    if not rows:
        return 0
    dates = {r["study_date"] for r in rows}
    streak = 0
    check_date = date.today()
    while str(check_date) in dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak


def get_total_study_days():
    conn = get_connection()
    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM streaks")
    conn.close()
    return (row or {}).get("c", 0) or 0


# ─────────────────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────────────────

def save_quiz_result(subject, chapter_title, difficulty, total, correct, time_taken=0):
    score_pct = (correct / total * 100) if total > 0 else 0
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO quiz_results
            (subject, chapter_title, difficulty, total_questions, correct_answers,
             score_percent, time_taken_seconds, quiz_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        (subject, chapter_title, difficulty, total, correct, score_pct, time_taken, today),
    )
    conn.commit()
    conn.close()
    add_points(correct * 10)

    # 🧠 Adaptive Learning Engine — auto-tune difficulty for next time.
    # Imported lazily to avoid a circular import (adaptive_engine imports db).
    try:
        if subject and chapter_title:
            from modules.adaptive_engine import update_after_quiz
            update_after_quiz(subject, chapter_title, score_pct)
    except Exception as _e:
        # Adaptive update should NEVER break the quiz flow
        print(f"adaptive update failed: {_e}")

    return score_pct


def save_question_attempt(subject, chapter, question, student_ans, correct_ans, is_correct, difficulty="Medium"):
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO question_history
            (subject, chapter_title, question, student_answer, correct_answer,
             is_correct, difficulty, attempt_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        (subject, chapter, question, student_ans, correct_ans, int(is_correct), difficulty, today),
    )
    conn.commit()
    conn.close()


def get_quiz_history(subject=None, limit=50):
    conn = get_connection()
    if subject:
        rows = _fetchall(
            conn,
            "SELECT * FROM quiz_results WHERE subject=? ORDER BY created_at DESC LIMIT ?",
            (subject, limit),
        )
    else:
        rows = _fetchall(conn, "SELECT * FROM quiz_results ORDER BY created_at DESC LIMIT ?", (limit,))
    conn.close()
    return rows


def get_weak_areas():
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT subject, chapter_title, AVG(score_percent) as avg_score, COUNT(*) as attempts
           FROM quiz_results
           GROUP BY subject, chapter_title
           HAVING AVG(score_percent) < 60
           ORDER BY avg_score ASC""",
    )
    conn.close()
    return rows


def get_subject_stats():
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT subject,
                  AVG(score_percent) as avg_score,
                  COUNT(*) as quiz_count,
                  SUM(correct_answers) as total_correct,
                  SUM(total_questions) as total_questions
           FROM quiz_results
           GROUP BY subject""",
    )
    conn.close()
    return {r["subject"]: r for r in rows}


# ─────────────────────────────────────────────────────────
# STUDY SESSIONS
# ─────────────────────────────────────────────────────────

def log_study_session(subject, chapter_id, chapter_title, duration_min, activity_type="learn"):
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO study_sessions
            (subject, chapter_id, chapter_title, duration_minutes, activity_type, session_date)
           VALUES (?,?,?,?,?,?)""",
        (subject, chapter_id, chapter_title, duration_min, activity_type, today),
    )
    conn.commit()
    conn.close()
    add_points(5)


def get_total_study_time():
    conn = get_connection()
    row = _fetchone(conn, "SELECT COALESCE(SUM(duration_minutes), 0) AS t FROM study_sessions")
    conn.close()
    return (row or {}).get("t", 0) or 0


def get_study_time_by_subject():
    conn = get_connection()
    rows = _fetchall(
        conn,
        "SELECT subject, SUM(duration_minutes) as total_minutes FROM study_sessions GROUP BY subject",
    )
    conn.close()
    return {r["subject"]: r["total_minutes"] for r in rows}


# ─────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────

def award_badge(badge_id, badge_name, badge_icon):
    today = str(date.today())
    conn = get_connection()
    try:
        if USE_PG:
            cur = _exec(
                conn,
                "INSERT INTO badges (badge_id, badge_name, badge_icon, earned_date) "
                "VALUES (?,?,?,?) ON CONFLICT (badge_id) DO NOTHING",
                (badge_id, badge_name, badge_icon, today),
            )
        else:
            cur = _exec(
                conn,
                "INSERT OR IGNORE INTO badges (badge_id, badge_name, badge_icon, earned_date) "
                "VALUES (?,?,?,?)",
                (badge_id, badge_name, badge_icon, today),
            )
        conn.commit()
        changed = cur.rowcount > 0
    except Exception:
        changed = False
    conn.close()
    return changed


def get_badges():
    conn = get_connection()
    rows = _fetchall(conn, "SELECT * FROM badges ORDER BY earned_date DESC")
    conn.close()
    return rows


def has_badge(badge_id):
    conn = get_connection()
    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM badges WHERE badge_id=?", (badge_id,))
    conn.close()
    return (row or {}).get("c", 0) > 0


# ─────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────

def save_chat_message(role, message, subject="general"):
    conn = get_connection()
    _exec(
        conn,
        "INSERT INTO chat_history (role, message, subject) VALUES (?,?,?)",
        (role, message, subject),
    )
    conn.commit()
    conn.close()


def get_chat_history(subject="general", limit=20):
    conn = get_connection()
    rows = _fetchall(
        conn,
        "SELECT role, message FROM chat_history WHERE subject=? ORDER BY created_at DESC LIMIT ?",
        (subject, limit),
    )
    conn.close()
    return list(reversed(rows))


def clear_chat_history(subject="general"):
    conn = get_connection()
    _exec(conn, "DELETE FROM chat_history WHERE subject=?", (subject,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# UPLOADED CONTENT
# ─────────────────────────────────────────────────────────

def save_uploaded_content(filename, subject, content_type, extracted_text, file_path):
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO uploaded_content
            (filename, subject, content_type, extracted_text, file_path, upload_date, processed)
           VALUES (?,?,?,?,?,?,1)""",
        (filename, subject, content_type, extracted_text, file_path, today),
    )
    conn.commit()
    conn.close()


def delete_uploaded_content(content_id):
    conn = get_connection()
    _exec(conn, "DELETE FROM uploaded_content WHERE id=?", (content_id,))
    conn.commit()
    conn.close()


def get_uploaded_content(subject=None):
    conn = get_connection()
    if subject:
        rows = _fetchall(
            conn,
            "SELECT * FROM uploaded_content WHERE subject=? ORDER BY upload_date DESC",
            (subject,),
        )
    else:
        rows = _fetchall(conn, "SELECT * FROM uploaded_content ORDER BY upload_date DESC")
    conn.close()
    return rows


# ─────────────────────────────────────────────────────────
# STUDY PLANNER
# ─────────────────────────────────────────────────────────

def save_study_plan(plan_date, subject, topic, duration_min=30, priority="Normal"):
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO study_plan (plan_date, subject, topic, duration_minutes, priority)
           VALUES (?,?,?,?,?)""",
        (plan_date, subject, topic, duration_min, priority),
    )
    conn.commit()
    conn.close()


def get_study_plan(plan_date=None):
    conn = get_connection()
    if plan_date:
        rows = _fetchall(
            conn,
            "SELECT * FROM study_plan WHERE plan_date=? ORDER BY priority DESC",
            (plan_date,),
        )
    else:
        rows = _fetchall(conn, "SELECT * FROM study_plan ORDER BY plan_date DESC, priority DESC")
    conn.close()
    return rows


def mark_plan_completed(plan_id):
    conn = get_connection()
    _exec(conn, "UPDATE study_plan SET completed=1 WHERE id=?", (plan_id,))
    conn.commit()
    conn.close()
    add_points(20)


# ─────────────────────────────────────────────────────────
# GAME SCORES
# ─────────────────────────────────────────────────────────

def save_game_score(game_name, score, level="Medium"):
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        "INSERT INTO game_scores (game_name, score, level, play_date) VALUES (?,?,?,?)",
        (game_name, score, level, today),
    )
    conn.commit()
    conn.close()
    add_points(score // 10 + 5)


def get_game_high_scores():
    conn = get_connection()
    rows = _fetchall(
        conn,
        "SELECT game_name, MAX(score) as high_score, COUNT(*) as plays "
        "FROM game_scores GROUP BY game_name",
    )
    conn.close()
    return {r["game_name"]: r for r in rows}


# ─────────────────────────────────────────────────────────
# CHAPTER PROGRESS
# ─────────────────────────────────────────────────────────

def mark_chapter_complete(subject, chapter_id, chapter_title):
    today = str(date.today())
    conn = get_connection()
    if USE_PG:
        _exec(
            conn,
            """INSERT INTO chapter_progress (subject, chapter_id, chapter_title, completed, completion_date)
               VALUES (?,?,?,1,?)
               ON CONFLICT (subject, chapter_id)
               DO UPDATE SET chapter_title=EXCLUDED.chapter_title,
                             completed=1,
                             completion_date=EXCLUDED.completion_date""",
            (subject, chapter_id, chapter_title, today),
        )
    else:
        _exec(
            conn,
            """INSERT OR REPLACE INTO chapter_progress
                (subject, chapter_id, chapter_title, completed, completion_date)
               VALUES (?,?,?,1,?)""",
            (subject, chapter_id, chapter_title, today),
        )
    conn.commit()
    conn.close()
    add_points(50)


def get_completed_chapters(subject=None):
    conn = get_connection()
    if subject:
        rows = _fetchall(
            conn,
            "SELECT * FROM chapter_progress WHERE subject=? AND completed=1",
            (subject,),
        )
    else:
        rows = _fetchall(conn, "SELECT * FROM chapter_progress WHERE completed=1")
    conn.close()
    return rows


# ─────────────────────────────────────────────────────────
# DOUBT HISTORY (Image Doubt Solver)
# ─────────────────────────────────────────────────────────

def save_doubt(subject, note, ai_response, image_filename="", image_size_kb=0):
    today = str(date.today())
    conn = get_connection()
    _exec(
        conn,
        """INSERT INTO doubt_history
            (subject, note, ai_response, image_filename, image_size_kb, doubt_date)
           VALUES (?,?,?,?,?,?)""",
        (subject, note, ai_response, image_filename, image_size_kb, today),
    )
    conn.commit()
    conn.close()
    add_points(5)


def get_doubt_history(limit=20):
    conn = get_connection()
    rows = _fetchall(
        conn,
        "SELECT * FROM doubt_history ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    conn.close()
    return rows


def delete_doubt(doubt_id):
    conn = get_connection()
    _exec(conn, "DELETE FROM doubt_history WHERE id=?", (doubt_id,))
    conn.commit()
    conn.close()


def get_doubt_count():
    conn = get_connection()
    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM doubt_history")
    conn.close()
    return (row or {}).get("c", 0) or 0


# ─────────────────────────────────────────────────────────
# ADAPTIVE PROFILE (Adaptive Learning Engine)
# ─────────────────────────────────────────────────────────

def get_adaptive_profile(subject, chapter_title):
    """Return the adaptive row for (subject, chapter), or None."""
    conn = get_connection()
    row = _fetchone(
        conn,
        "SELECT * FROM adaptive_profile WHERE subject=? AND chapter_title=?",
        (subject, chapter_title),
    )
    conn.close()
    return row


def upsert_adaptive_profile(subject, chapter_title, current_level,
                            last_accuracy, recommended_action, attempts_delta=1):
    """Insert or update the adaptive profile row for (subject, chapter)."""
    conn = get_connection()
    existing = _fetchone(
        conn,
        "SELECT attempts FROM adaptive_profile WHERE subject=? AND chapter_title=?",
        (subject, chapter_title),
    )
    new_attempts = (existing or {}).get("attempts", 0) + attempts_delta if existing else attempts_delta

    if USE_PG:
        _exec(
            conn,
            """INSERT INTO adaptive_profile
                (subject, chapter_title, current_level, last_accuracy, attempts, recommended_action, updated_at)
               VALUES (?,?,?,?,?,?, NOW())
               ON CONFLICT (subject, chapter_title)
               DO UPDATE SET current_level=EXCLUDED.current_level,
                             last_accuracy=EXCLUDED.last_accuracy,
                             attempts=EXCLUDED.attempts,
                             recommended_action=EXCLUDED.recommended_action,
                             updated_at=NOW()""",
            (subject, chapter_title, current_level, last_accuracy, new_attempts, recommended_action),
        )
    else:
        # SQLite path: rely on UNIQUE + REPLACE
        _exec(
            conn,
            """INSERT OR REPLACE INTO adaptive_profile
                (id, subject, chapter_title, current_level, last_accuracy, attempts, recommended_action, updated_at)
               VALUES (
                 (SELECT id FROM adaptive_profile WHERE subject=? AND chapter_title=?),
                 ?,?,?,?,?,?, CURRENT_TIMESTAMP)""",
            (subject, chapter_title,
             subject, chapter_title, current_level, last_accuracy, new_attempts, recommended_action),
        )
    conn.commit()
    conn.close()


def get_all_adaptive_profiles():
    conn = get_connection()
    rows = _fetchall(conn, "SELECT * FROM adaptive_profile ORDER BY updated_at DESC")
    conn.close()
    return rows


# ─────────────────────────────────────────────────────────
# ANALYTICS — time-windowed views for the Parent Dashboard
# ─────────────────────────────────────────────────────────

def _date_range(days: int) -> list[str]:
    """Return YYYY-MM-DD strings from (days-1) ago up to today, ascending."""
    today = date.today()
    return [str(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]


def get_study_minutes_by_day(days: int = 7) -> dict:
    """Total study minutes per date for the last N days. Includes zero-days."""
    range_dates = _date_range(days)
    cutoff = range_dates[0]
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT session_date, COALESCE(SUM(duration_minutes), 0) AS m
           FROM study_sessions
           WHERE session_date >= ?
           GROUP BY session_date""",
        (cutoff,),
    )
    conn.close()
    by_day = {r["session_date"]: int(r["m"] or 0) for r in rows}
    return {d: by_day.get(d, 0) for d in range_dates}


def get_quiz_count_by_day(days: int = 7) -> dict:
    range_dates = _date_range(days)
    cutoff = range_dates[0]
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT quiz_date, COUNT(*) AS c
           FROM quiz_results
           WHERE quiz_date >= ?
           GROUP BY quiz_date""",
        (cutoff,),
    )
    conn.close()
    by_day = {r["quiz_date"]: int(r["c"] or 0) for r in rows}
    return {d: by_day.get(d, 0) for d in range_dates}


def get_avg_quiz_score_by_day(days: int = 7) -> dict:
    range_dates = _date_range(days)
    cutoff = range_dates[0]
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT quiz_date, AVG(score_percent) AS s
           FROM quiz_results
           WHERE quiz_date >= ?
           GROUP BY quiz_date""",
        (cutoff,),
    )
    conn.close()
    by_day = {r["quiz_date"]: float(r["s"] or 0) for r in rows}
    return {d: round(by_day.get(d, 0), 1) for d in range_dates}


def get_doubt_count_by_day(days: int = 7) -> dict:
    range_dates = _date_range(days)
    cutoff = range_dates[0]
    conn = get_connection()
    rows = _fetchall(
        conn,
        """SELECT doubt_date, COUNT(*) AS c
           FROM doubt_history
           WHERE doubt_date >= ?
           GROUP BY doubt_date""",
        (cutoff,),
    )
    conn.close()
    by_day = {r["doubt_date"]: int(r["c"] or 0) for r in rows}
    return {d: by_day.get(d, 0) for d in range_dates}


def get_week_summary(days: int = 7) -> dict:
    """High-level totals for the last N days."""
    sm = get_study_minutes_by_day(days)
    qc = get_quiz_count_by_day(days)
    ds = get_doubt_count_by_day(days)
    avg_scores = get_avg_quiz_score_by_day(days)
    # Compute avg score weighted by quiz count
    total_quizzes = sum(qc.values())
    if total_quizzes > 0:
        weighted = sum(avg_scores[d] * qc[d] for d in qc)
        avg_score = round(weighted / total_quizzes, 1) if total_quizzes else 0
    else:
        avg_score = 0

    return {
        "study_minutes": sum(sm.values()),
        "quizzes_taken": total_quizzes,
        "avg_score": avg_score,
        "doubts_solved": sum(ds.values()),
        "active_days": sum(1 for d in sm if sm[d] > 0 or qc[d] > 0 or ds[d] > 0),
        "study_minutes_by_day": sm,
        "quizzes_by_day": qc,
        "doubts_by_day": ds,
        "avg_score_by_day": avg_scores,
    }


def get_week_comparison(days: int = 7) -> dict:
    """Returns this week's totals AND last week's totals for diff display."""
    today = date.today()
    this_cutoff = str(today - timedelta(days=days - 1))
    last_start = str(today - timedelta(days=2 * days - 1))
    last_end = str(today - timedelta(days=days))

    conn = get_connection()
    this_minutes = (_fetchone(
        conn,
        "SELECT COALESCE(SUM(duration_minutes), 0) AS m FROM study_sessions WHERE session_date >= ?",
        (this_cutoff,),
    ) or {}).get("m") or 0
    last_minutes = (_fetchone(
        conn,
        "SELECT COALESCE(SUM(duration_minutes), 0) AS m FROM study_sessions WHERE session_date >= ? AND session_date <= ?",
        (last_start, last_end),
    ) or {}).get("m") or 0

    this_quizzes = (_fetchone(
        conn,
        "SELECT COUNT(*) AS c FROM quiz_results WHERE quiz_date >= ?",
        (this_cutoff,),
    ) or {}).get("c") or 0
    last_quizzes = (_fetchone(
        conn,
        "SELECT COUNT(*) AS c FROM quiz_results WHERE quiz_date >= ? AND quiz_date <= ?",
        (last_start, last_end),
    ) or {}).get("c") or 0

    this_score_row = _fetchone(
        conn,
        "SELECT AVG(score_percent) AS s FROM quiz_results WHERE quiz_date >= ?",
        (this_cutoff,),
    )
    last_score_row = _fetchone(
        conn,
        "SELECT AVG(score_percent) AS s FROM quiz_results WHERE quiz_date >= ? AND quiz_date <= ?",
        (last_start, last_end),
    )
    this_avg = round(float((this_score_row or {}).get("s") or 0), 1)
    last_avg = round(float((last_score_row or {}).get("s") or 0), 1)
    conn.close()

    return {
        "this_minutes": int(this_minutes), "last_minutes": int(last_minutes),
        "this_quizzes": int(this_quizzes), "last_quizzes": int(last_quizzes),
        "this_avg_score": this_avg,        "last_avg_score": last_avg,
    }


def get_recent_activity_log(limit: int = 15) -> list:
    """Mixed-source recent activity, newest first.
    Each event: {ts, kind, subject, label, detail}."""
    conn = get_connection()
    quizzes = _fetchall(
        conn,
        """SELECT created_at AS ts, subject, chapter_title, score_percent,
                  correct_answers, total_questions
           FROM quiz_results ORDER BY created_at DESC LIMIT ?""",
        (limit,),
    )
    sessions = _fetchall(
        conn,
        """SELECT created_at AS ts, subject, chapter_title, duration_minutes, activity_type
           FROM study_sessions ORDER BY created_at DESC LIMIT ?""",
        (limit,),
    )
    chapters = _fetchall(
        conn,
        """SELECT completion_date AS ts, subject, chapter_title
           FROM chapter_progress WHERE completed=1
           ORDER BY completion_date DESC LIMIT ?""",
        (limit,),
    )
    doubts = _fetchall(
        conn,
        """SELECT created_at AS ts, subject, image_filename, note
           FROM doubt_history ORDER BY created_at DESC LIMIT ?""",
        (limit,),
    )
    badges_rows = _fetchall(
        conn,
        """SELECT earned_date AS ts, badge_id, badge_name, badge_icon
           FROM badges ORDER BY earned_date DESC LIMIT ?""",
        (limit,),
    )
    conn.close()

    events = []
    for r in quizzes:
        events.append({
            "ts": r.get("ts") or "",
            "kind": "quiz",
            "subject": r.get("subject") or "",
            "label": f"📝 Quiz: {r.get('chapter_title', '')}",
            "detail": f"Score {round(float(r.get('score_percent') or 0))}% "
                      f"({r.get('correct_answers')}/{r.get('total_questions')})",
        })
    for r in sessions:
        events.append({
            "ts": r.get("ts") or "",
            "kind": "study",
            "subject": r.get("subject") or "",
            "label": f"📖 Studied: {r.get('chapter_title', '')}",
            "detail": f"{r.get('duration_minutes') or 0} min ({r.get('activity_type') or 'learn'})",
        })
    for r in chapters:
        events.append({
            "ts": r.get("ts") or "",
            "kind": "chapter",
            "subject": r.get("subject") or "",
            "label": f"✅ Chapter completed: {r.get('chapter_title', '')}",
            "detail": "",
        })
    for r in doubts:
        events.append({
            "ts": r.get("ts") or "",
            "kind": "doubt",
            "subject": r.get("subject") or "",
            "label": f"📸 Doubt solved",
            "detail": (r.get("note") or r.get("image_filename") or "")[:80],
        })
    for r in badges_rows:
        events.append({
            "ts": r.get("ts") or "",
            "kind": "badge",
            "subject": "",
            "label": f"{r.get('badge_icon') or '🏅'} New badge: {r.get('badge_name') or ''}",
            "detail": "",
        })

    # Sort newest first by ts string (works for ISO timestamps and YYYY-MM-DD)
    events.sort(key=lambda e: str(e.get("ts") or ""), reverse=True)
    return events[:limit]


# ─────────────────────────────────────────────────────────
# DASHBOARD SUMMARY
# ─────────────────────────────────────────────────────────

def get_dashboard_summary():
    return {
        "student": get_student(),
        "points": get_total_points(),
        "streak": get_current_streak(),
        "study_days": get_total_study_days(),
        "total_study_time": get_total_study_time(),
        "badges": get_badges(),
        "badges_count": len(get_badges()),
        "weak_areas": get_weak_areas(),
        "subject_stats": get_subject_stats(),
        "quiz_count": len(get_quiz_history()),
        "completed_chapters": len(get_completed_chapters()),
        "study_time_by_subject": get_study_time_by_subject(),
    }
