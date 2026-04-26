"""
Quiz Engine - Generate, manage, and score quizzes
"""

import random
import time
from utils.config import get_subject, get_syllabus, DIFFICULTY_LEVELS
from modules.ai_engine import generate_questions

# ─────────────────────────────────────────────────────────
# QUIZ BUILDER
# ─────────────────────────────────────────────────────────

def build_quiz(subject, chapter_title, difficulty="Medium", count=5, api_key="",
               uploaded_text=""):
    """
    Build a complete quiz.
    Returns list of question dicts with 'question', 'answer', 'type', 'options'.
    """
    questions = generate_questions(
        subject=subject,
        chapter=chapter_title,
        difficulty=difficulty,
        count=count,
        api_key=api_key,
        uploaded_content=uploaded_text
    )

    # Enrich questions
    enriched = []
    for i, q in enumerate(questions):
        q["id"] = i + 1
        q["subject"] = subject
        q["chapter"] = chapter_title
        q["difficulty"] = difficulty
        q["answered"] = False
        q["student_answer"] = ""
        q["is_correct"] = False
        enriched.append(q)

    return enriched


def score_quiz(questions):
    """
    Calculate score from answered questions.
    Returns (correct_count, total, percentage, results_list)
    """
    correct = 0
    results = []

    for q in questions:
        student_ans = q.get("student_answer", "").strip().lower()
        correct_ans = q.get("answer", "").strip().lower()

        # Flexible matching
        is_correct = _check_answer(student_ans, correct_ans)
        q["is_correct"] = is_correct
        if is_correct:
            correct += 1

        results.append({
            "question": q["question"],
            "student_answer": q.get("student_answer", ""),
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "difficulty": q.get("difficulty", "Medium")
        })

    total = len(questions)
    percentage = (correct / total * 100) if total > 0 else 0
    return correct, total, percentage, results


def _check_answer(student_ans, correct_ans):
    """
    Flexible answer checking - handles partial matches.
    """
    if not student_ans:
        return False

    # Exact match
    if student_ans == correct_ans:
        return True

    # Clean both answers
    student_clean = _clean_answer(student_ans)
    correct_clean = _clean_answer(correct_ans)

    if student_clean == correct_clean:
        return True

    # Check if student answer contains key parts of correct answer
    correct_words = set(correct_clean.split())
    student_words = set(student_clean.split())

    # Remove common words
    stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'it', 'of', 'in', 'on', 'at', 'to', 'and', 'or'}
    correct_key = correct_words - stop_words
    student_key = student_words - stop_words

    if not correct_key:
        return False

    # If 60%+ of key words match, consider correct
    overlap = len(correct_key & student_key)
    if overlap / len(correct_key) >= 0.6:
        return True

    # Number check
    import re
    correct_nums = set(re.findall(r'\d+\.?\d*', correct_clean))
    student_nums = set(re.findall(r'\d+\.?\d*', student_clean))
    if correct_nums and correct_nums == student_nums:
        return True

    return False


def _clean_answer(ans):
    """Clean answer for comparison."""
    import re
    ans = ans.lower()
    ans = re.sub(r'[^\w\s\d\.]', ' ', ans)
    ans = re.sub(r'\s+', ' ', ans).strip()
    return ans


# ─────────────────────────────────────────────────────────
# RAPID FIRE QUIZ
# ─────────────────────────────────────────────────────────

def get_rapid_fire_questions(subject=None, count=20):
    """Get quick true/false or very short questions for rapid fire mode."""
    SYLLABUS = get_syllabus()         # 🧠 Live curriculum (Phase 4)
    rapid_questions = []

    subjects_to_use = [subject] if subject else list(SYLLABUS.keys())[:5]

    for subj in subjects_to_use:
        subj_data = SYLLABUS.get(subj, {})
        for chapter in subj_data.get("chapters", []):
            for q in chapter.get("questions", []):
                if q.get("type") in ("short", "identify", "calculate"):
                    rapid_questions.append({
                        "question": q["q"],
                        "answer": q["a"],
                        "subject": subj,
                        "chapter": chapter["title"],
                        "type": "rapid"
                    })

    random.shuffle(rapid_questions)
    return rapid_questions[:count]


# ─────────────────────────────────────────────────────────
# MCQ GENERATOR
# ─────────────────────────────────────────────────────────

def get_mcq_questions(subject, chapter_title, count=5):
    """Get MCQ format questions."""
    SYLLABUS = get_syllabus()         # 🧠 Live curriculum (Phase 4)
    subj_data = SYLLABUS.get(subject, {})
    mcq_questions = []

    for chapter in subj_data.get("chapters", []):
        for q in chapter.get("questions", []):
            if q.get("type") == "mcq" and q.get("options"):
                mcq_questions.append({
                    "question": q["q"],
                    "answer": q["a"],
                    "options": q["options"],
                    "subject": subject,
                    "chapter": chapter["title"]
                })

    # If not enough MCQ questions, convert short-answer questions to MCQ
    if len(mcq_questions) < count:
        for chapter in subj_data.get("chapters", []):
            if chapter["title"].lower() in chapter_title.lower() or chapter_title.lower() in chapter["title"].lower():
                for q in chapter.get("questions", []):
                    if q.get("type") != "mcq":
                        fake_mcq = _make_fake_mcq(q["q"], q["a"])
                        mcq_questions.append({
                            "question": q["q"],
                            "answer": q["a"],
                            "options": fake_mcq,
                            "subject": subject,
                            "chapter": chapter["title"]
                        })

    random.shuffle(mcq_questions)
    return mcq_questions[:count]


def _make_fake_mcq(question, correct_answer):
    """Create fake MCQ options with the correct answer mixed in."""
    distractors = [
        "None of the above",
        "All of the above",
        "Cannot be determined",
        "Not mentioned in syllabus"
    ]

    options = [correct_answer]
    for d in distractors[:3]:
        options.append(d)

    random.shuffle(options)
    return options


# ─────────────────────────────────────────────────────────
# PRACTICE TEST BUILDER
# ─────────────────────────────────────────────────────────

def build_practice_test(subject, difficulty="Mixed", num_questions=10, api_key=""):
    """Build a full practice test from all chapters of a subject."""
    SYLLABUS = get_syllabus()         # 🧠 Live curriculum (Phase 4)
    subj_data = SYLLABUS.get(subject, {})
    chapters = subj_data.get("chapters", [])

    if not chapters:
        return []

    all_questions = []
    questions_per_chapter = max(1, num_questions // len(chapters))

    for chapter in chapters:
        if difficulty == "Mixed":
            diff = random.choice(DIFFICULTY_LEVELS)
        else:
            diff = difficulty

        qs = build_quiz(
            subject=subject,
            chapter_title=chapter["title"],
            difficulty=diff,
            count=questions_per_chapter,
            api_key=api_key
        )
        all_questions.extend(qs)

    random.shuffle(all_questions)
    return all_questions[:num_questions]


# ─────────────────────────────────────────────────────────
# QUESTION FROM UPLOADED CONTENT
# ─────────────────────────────────────────────────────────

def generate_from_uploaded(subject, uploaded_text, difficulty="Medium", count=5, api_key=""):
    """Generate questions specifically from uploaded textbook/paper content."""
    return generate_questions(
        subject=subject,
        chapter=f"Uploaded Content - {get_subject(subject)['name']}",
        difficulty=difficulty,
        count=count,
        api_key=api_key,
        uploaded_content=uploaded_text
    )
