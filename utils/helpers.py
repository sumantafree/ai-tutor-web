"""
Helper utilities for AI Home Tutor
"""

import random
import os
import hashlib
from datetime import datetime
from utils.config import MOTIVATIONAL_MESSAGES, BADGES, DATA_DIR

def get_motivation():
    """Return a random motivational message."""
    return random.choice(MOTIVATIONAL_MESSAGES)

def format_time(minutes):
    """Convert minutes to human-readable format."""
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours} hr"
    return f"{hours} hr {mins} min"

def get_grade_emoji(score_pct):
    """Return grade emoji based on score percentage."""
    if score_pct >= 90:
        return "🌟 Excellent!"
    elif score_pct >= 75:
        return "✅ Very Good!"
    elif score_pct >= 60:
        return "👍 Good!"
    elif score_pct >= 40:
        return "📖 Keep Practicing!"
    else:
        return "💪 Don't Give Up!"

def get_score_color(score_pct):
    """Return color for score display."""
    if score_pct >= 75:
        return "#00B894"   # green
    elif score_pct >= 50:
        return "#FDCB6E"   # yellow
    else:
        return "#E17055"   # red

def check_and_award_badges(db_module):
    """Check conditions and award badges. Returns list of newly awarded badges."""
    new_badges = []
    quiz_count   = len(db_module.get_quiz_history())
    streak       = db_module.get_current_streak()
    badges_owned = {b["badge_id"] for b in db_module.get_badges()}
    stats        = db_module.get_subject_stats()
    completed    = db_module.get_completed_chapters()
    study_sessions_count = len(db_module.get_quiz_history())

    # Build condition map
    conditions = [
        ("first_lesson", len(completed) >= 1, "First Step!",     "🌱"),
        ("quiz_5",       quiz_count >= 5,    "Quiz Starter",     "📝"),
        ("quiz_20",      quiz_count >= 20,   "Quiz Champion",    "🏆"),
        ("streak_3",     streak >= 3,        "3-Day Streak!",    "🔥"),
        ("streak_7",     streak >= 7,        "Week Warrior!",    "🔥🔥"),
        ("bookworm",     len(completed) >= 10, "Bookworm",       "📚"),
    ]

    # Check maths mastery
    if "mathematics" in stats and stats["mathematics"]["avg_score"] >= 90:
        conditions.append(("math_master", True, "Math Master", "🔢"))

    for badge_id, condition, name, icon in conditions:
        if condition and badge_id not in badges_owned:
            awarded = db_module.award_badge(badge_id, name, icon)
            if awarded:
                new_badges.append({"badge_id": badge_id, "badge_name": name, "badge_icon": icon})

    return new_badges

def safe_filename(name):
    """Convert a string to a safe filename."""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)

def truncate_text(text, max_chars=200):
    """Truncate text to max_chars with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."

def ensure_data_dirs():
    """Ensure all required data directories exist."""
    dirs = [
        os.path.join(DATA_DIR, "syllabus"),
        os.path.join(DATA_DIR, "books"),
        os.path.join(DATA_DIR, "previous_papers"),
        os.path.join(DATA_DIR, "processed"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def get_subject_folder(subject_id):
    """Return the folder path for a subject's books."""
    return os.path.join(DATA_DIR, "books", subject_id)

def get_difficulty_color(difficulty):
    colors = {"Easy": "#00B894", "Medium": "#FDCB6E", "Hard": "#E17055"}
    return colors.get(difficulty, "#74B9FF")

def get_difficulty_points(difficulty):
    points = {"Easy": 5, "Medium": 10, "Hard": 20}
    return points.get(difficulty, 10)

def get_day_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"
