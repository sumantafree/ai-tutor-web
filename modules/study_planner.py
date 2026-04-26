"""
Study Planner - Daily study planning and scheduling
"""

import random
from datetime import date, timedelta
from utils.config import get_subjects, get_syllabus

# ─────────────────────────────────────────────────────────
# AUTO PLANNER
# ─────────────────────────────────────────────────────────

def generate_daily_plan(weak_areas=None, study_days_per_week=5, daily_hours=2):
    """
    Generate a smart weekly study plan.
    Returns list of plan items for the next 7 days.
    """
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)
    SYLLABUS = get_syllabus()
    plan = []
    today = date.today()
    daily_minutes = daily_hours * 60

    # Priority: weak areas first, then all subjects
    subject_ids = [s["id"] for s in SUBJECTS]
    if weak_areas:
        weak_subjects = [w["subject"] for w in weak_areas]
        # Move weak subjects to front
        subject_ids = weak_subjects + [s for s in subject_ids if s not in weak_subjects]

    # Get all chapters per subject
    all_topics = []
    for subj_id in subject_ids:
        subj_data = SYLLABUS.get(subj_id, {})
        for chapter in subj_data.get("chapters", []):
            is_weak = weak_areas and any(
                w["subject"] == subj_id and w["chapter_title"] == chapter["title"]
                for w in weak_areas
            )
            all_topics.append({
                "subject": subj_id,
                "topic": chapter["title"],
                "duration": 30 if not is_weak else 45,
                "priority": "High" if is_weak else "Normal"
            })

    # Distribute over days
    day_count = 0
    topic_idx = 0
    for day_offset in range(7):
        plan_date = today + timedelta(days=day_offset)
        weekday = plan_date.weekday()  # 0=Mon, 6=Sun

        # Skip some days based on study_days_per_week
        if study_days_per_week <= 5 and weekday >= 5:
            continue  # Skip weekend

        if study_days_per_week <= 3 and weekday in [1, 3, 5, 6]:
            continue

        day_count += 1
        minutes_used = 0

        while minutes_used < daily_minutes and topic_idx < len(all_topics):
            topic = all_topics[topic_idx % len(all_topics)]
            if minutes_used + topic["duration"] > daily_minutes:
                break
            plan.append({
                "date": str(plan_date),
                "subject": topic["subject"],
                "topic": topic["topic"],
                "duration_minutes": topic["duration"],
                "priority": topic["priority"],
                "completed": False
            })
            minutes_used += topic["duration"]
            topic_idx += 1

    return plan


def get_today_plan_items(all_plans):
    """Filter plan items for today."""
    today = str(date.today())
    return [p for p in all_plans if p.get("plan_date") == today or p.get("date") == today]


def get_study_tips(subject=None):
    """Return study tips for a subject or general tips."""
    general_tips = [
        "📚 Study in short sessions of 25-30 minutes with 5-minute breaks (Pomodoro technique)!",
        "✏️ Write notes in your own words - it helps you remember better!",
        "🔄 Review yesterday's notes before starting new topics.",
        "😴 Get 8-9 hours of sleep - your brain consolidates learning during sleep!",
        "🎯 Set a small goal before each study session: 'Today I will learn Chapter 3'",
        "❓ Ask yourself questions while reading - 'Why?', 'How?', 'What if?'",
        "🏃 Take movement breaks - a 5-minute walk refreshes your brain!",
        "🎵 Light background music can help concentration (no lyrics!)",
        "📱 Keep your phone away during study time - you can do it!",
        "🌟 Reward yourself after completing each chapter with something you enjoy!",
    ]

    subject_tips = {
        "mathematics": [
            "🔢 Practice 5-10 math problems daily - consistency is key!",
            "📐 Always show your working - even if the answer is wrong, you get marks!",
            "✅ Check answers by working backwards",
            "📊 Make formula sheets and review them regularly",
        ],
        "english": [
            "📖 Read English books/comics for 15 minutes daily",
            "📝 Learn 5 new vocabulary words each day",
            "✍️ Write a short diary entry in English daily",
        ],
        "biology": [
            "🔬 Draw and label diagrams - it helps memorize structures",
            "🌿 Use mnemonics for classification and processes",
            "🔄 Connect concepts to real life (cell → body, photosynthesis → cooking)",
        ],
        "history": [
            "📅 Make a timeline of events on paper",
            "🗺️ Always study history with a map nearby",
            "📖 Learn the 'story' - not just dates, but WHY things happened",
        ],
        "geography": [
            "🗺️ Draw maps and label them frequently",
            "🌍 Use mnemonics for capitals and locations",
            "👀 Watch geography videos/documentaries when possible",
        ],
    }

    tips = []
    if subject and subject in subject_tips:
        tips = subject_tips[subject] + general_tips[:3]
    else:
        tips = general_tips

    random.shuffle(tips)
    return tips[:5]


def get_revision_schedule(weak_areas):
    """Create a focused revision schedule for weak areas."""
    if not weak_areas:
        return []

    schedule = []
    today = date.today()

    for i, area in enumerate(weak_areas[:6]):  # Max 6 weak areas
        revision_date = today + timedelta(days=i // 2)
        schedule.append({
            "date": str(revision_date),
            "subject": area["subject"],
            "topic": area["chapter_title"],
            "type": "Revision",
            "priority": "High",
            "avg_score": area.get("avg_score", 0),
            "duration_minutes": 45
        })

    return schedule
