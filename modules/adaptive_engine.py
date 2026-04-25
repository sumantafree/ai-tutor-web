"""
🧠 Adaptive Learning Engine
===========================
Personalises difficulty and AI-tutor tone per (subject, chapter) based on
the student's recent quiz accuracy.

Rules (from product spec):
    accuracy > 80%        → Advance        → bump level up
    50% <= accuracy <= 80% → Practice       → keep current level
    accuracy < 50%        → Revise         → drop level down

State lives in `adaptive_profile` table (utils/database.py).
"""

from typing import Optional, Tuple
import utils.database as db

LEVELS = ["Easy", "Medium", "Hard"]
DEFAULT_LEVEL = "Medium"
DEFAULT_ACTION = "Practice"

# Visual hints used by UI badges
LEVEL_COLORS = {
    "Easy":   "#00B894",   # green
    "Medium": "#FDCB6E",   # amber
    "Hard":   "#E17055",   # red-orange
}
ACTION_ICON = {
    "Revise":   "📖",
    "Practice": "📝",
    "Advance":  "🚀",
}
ACTION_BG = {
    "Revise":   "#FFE5E5",
    "Practice": "#F0F0FF",
    "Advance":  "#E5F8F3",
}


# ─────────────────────────────────────────────────────────
# CORE RULES
# ─────────────────────────────────────────────────────────

def _bump(level: str, direction: int) -> str:
    """direction = +1 for up, -1 for down. Clamped to [Easy..Hard]."""
    try:
        idx = LEVELS.index(level)
    except ValueError:
        idx = LEVELS.index(DEFAULT_LEVEL)
    new_idx = max(0, min(len(LEVELS) - 1, idx + direction))
    return LEVELS[new_idx]


def decide(current_level: str, accuracy_pct: float) -> Tuple[str, str]:
    """Pure function. Given current level + last accuracy %, return
    (new_level, recommended_action)."""
    if accuracy_pct > 80:
        return _bump(current_level, +1), "Advance"
    if accuracy_pct < 50:
        return _bump(current_level, -1), "Revise"
    return current_level, "Practice"


# ─────────────────────────────────────────────────────────
# STATE I/O
# ─────────────────────────────────────────────────────────

def get_profile(subject: str, chapter_title: str) -> dict:
    """Return the adaptive profile, falling back to sensible defaults."""
    if not subject or not chapter_title:
        return _default_profile(subject, chapter_title)
    row = db.get_adaptive_profile(subject, chapter_title)
    if not row:
        return _default_profile(subject, chapter_title)
    # Normalise types
    row["current_level"] = row.get("current_level") or DEFAULT_LEVEL
    row["recommended_action"] = row.get("recommended_action") or DEFAULT_ACTION
    row["last_accuracy"] = float(row.get("last_accuracy") or 0)
    row["attempts"] = int(row.get("attempts") or 0)
    return row


def _default_profile(subject, chapter_title) -> dict:
    return {
        "subject": subject or "",
        "chapter_title": chapter_title or "",
        "current_level": DEFAULT_LEVEL,
        "last_accuracy": 0.0,
        "attempts": 0,
        "recommended_action": DEFAULT_ACTION,
    }


def update_after_quiz(subject: str, chapter_title: str,
                      accuracy_pct: float) -> dict:
    """Apply the rule + persist. Returns the updated profile."""
    if not subject or not chapter_title:
        return _default_profile(subject, chapter_title)

    current = get_profile(subject, chapter_title)
    new_level, action = decide(current["current_level"], accuracy_pct)

    db.upsert_adaptive_profile(
        subject=subject,
        chapter_title=chapter_title,
        current_level=new_level,
        last_accuracy=float(accuracy_pct),
        recommended_action=action,
        attempts_delta=1,
    )
    return {
        **current,
        "current_level": new_level,
        "last_accuracy": float(accuracy_pct),
        "attempts": current["attempts"] + 1,
        "recommended_action": action,
        "previous_level": current["current_level"],
        "level_changed": new_level != current["current_level"],
    }


# ─────────────────────────────────────────────────────────
# PROMPT INJECTION
# ─────────────────────────────────────────────────────────

def level_to_prompt_addon(level: str) -> str:
    """Snippet appended to the system prompt so the AI matches the student."""
    if level == "Easy":
        return (
            "\n\nStudent profile: BEGINNER on this topic.\n"
            "- Use the simplest possible words.\n"
            "- Give MORE examples and analogies than usual.\n"
            "- Break each step into smaller sub-steps.\n"
            "- Never say 'obviously' or 'clearly' — they are still learning."
        )
    if level == "Hard":
        return (
            "\n\nStudent profile: ADVANCED on this topic.\n"
            "- Skip the basics; assume they understand them.\n"
            "- Give a slightly tougher example or twist.\n"
            "- End with a CHALLENGE follow-up question (one they have to think about)."
        )
    # Medium / unknown
    return (
        "\n\nStudent profile: ON-LEVEL.\n"
        "- Standard difficulty, one clear example, encouraging tone."
    )


def context_addon_for(subject: str, chapter_title: str) -> str:
    """Convenience: fetch profile and return the prompt addon for it."""
    if not subject or not chapter_title:
        return ""
    profile = get_profile(subject, chapter_title)
    return level_to_prompt_addon(profile["current_level"])


# ─────────────────────────────────────────────────────────
# UI HELPERS (pure HTML strings — UI module renders them)
# ─────────────────────────────────────────────────────────

def render_badge_html(profile: dict) -> str:
    """Return a small HTML badge showing 'Difficulty: X • Recommended: Y'."""
    level = profile.get("current_level", DEFAULT_LEVEL)
    action = profile.get("recommended_action", DEFAULT_ACTION)
    acc = profile.get("last_accuracy", 0)
    attempts = profile.get("attempts", 0)
    level_color = LEVEL_COLORS.get(level, "#74B9FF")
    action_bg = ACTION_BG.get(action, "#F0F0FF")
    action_icon = ACTION_ICON.get(action, "📝")

    sub = (
        f"based on {attempts} attempt{'s' if attempts != 1 else ''}, "
        f"last score {acc:.0f}%"
        if attempts > 0 else
        "no attempts yet — Adaptive Engine starts after your first quiz"
    )

    return f"""
    <div style="display:flex; gap:0.6rem; flex-wrap:wrap; align-items:center;
                margin: 0.4rem 0 0.8rem; padding:0.6rem 0.9rem;
                background:#F8F9FF; border:1px solid #E0E3FF;
                border-radius:12px; font-size:0.95rem;">
      <span style="background:{level_color}; color:white;
                   padding:3px 10px; border-radius:999px;
                   font-weight:700;">
        🎯 Difficulty: {level}
      </span>
      <span style="background:{action_bg}; color:#2d3436;
                   padding:3px 10px; border-radius:999px;
                   font-weight:600;">
        {action_icon} Recommended: {action}
      </span>
      <span style="color:#636e72; font-size:0.85rem;">{sub}</span>
    </div>
    """


def render_change_banner_html(updated_profile: dict) -> Optional[str]:
    """After a quiz, show a celebratory or supportive banner about the level change."""
    if not updated_profile.get("level_changed"):
        return None
    prev = updated_profile.get("previous_level", DEFAULT_LEVEL)
    new = updated_profile["current_level"]
    action = updated_profile["recommended_action"]
    if action == "Advance":
        return (
            f'<div style="background:linear-gradient(135deg,#55efc4,#00b894); '
            f'color:white; padding:1rem 1.2rem; border-radius:12px; '
            f'margin:0.8rem 0; font-weight:600;">'
            f"🚀 Level Up! Difficulty raised from <b>{prev}</b> → <b>{new}</b>. "
            f"You're getting really good at this topic!"
            f"</div>"
        )
    if action == "Revise":
        return (
            f'<div style="background:linear-gradient(135deg,#FFE5E5,#FDCB6E); '
            f'color:#2d3436; padding:1rem 1.2rem; border-radius:12px; '
            f'margin:0.8rem 0; font-weight:600;">'
            f"📖 No worries — difficulty lowered from <b>{prev}</b> → <b>{new}</b>. "
            f"Let's revise this chapter and try again!"
            f"</div>"
        )
    return None
