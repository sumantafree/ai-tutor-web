"""
AI Engine - Handles all AI interactions
Uses Google Gemini API when key is available, falls back to built-in responses.
"""

import os
import random
from utils.config import AI_SYSTEM_PROMPT, get_subject, get_syllabus

# Default model — Gemini 2.5 Flash is fast and free-tier-friendly.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def is_valid_gemini_key(key: str) -> bool:
    """Gemini API keys from Google AI Studio start with 'AIza'."""
    if not key:
        return False
    key = key.strip()
    return key.startswith("AIza") and len(key) >= 30


def _get_gemini_client(api_key):
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        return None
    except Exception:
        return None


def _gemini_config(system_prompt):
    try:
        from google.genai import types
        return types.GenerateContentConfig(system_instruction=system_prompt)
    except Exception:
        return None


def _resolve_api_key(api_key: str) -> str:
    """Prefer caller-provided key, else fall back to env var."""
    key = (api_key or "").strip()
    if is_valid_gemini_key(key):
        return key
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if is_valid_gemini_key(env_key):
        return env_key
    return ""


def _adaptive_addon(subject: str, chapter_title: str) -> str:
    """Return the Adaptive Engine prompt addon, or '' if not applicable.
    Lazy import + try/except so AI never breaks if the engine isn't wired."""
    try:
        if not subject or not chapter_title:
            return ""
        from modules.adaptive_engine import context_addon_for
        return context_addon_for(subject, chapter_title) or ""
    except Exception:
        return ""


def ask_tutor(question, subject="general", chapter_context="", history=None,
              api_key="", chapter_title=""):
    """Ask the AI tutor a question. Returns (answer_text, used_ai: bool).

    `chapter_title` is optional — when provided we inject the Adaptive Engine
    addon so the AI matches the student's current difficulty level.
    """
    if not question.strip():
        return "Please type your question! 😊", False

    key = _resolve_api_key(api_key)
    if key:
        try:
            system = AI_SYSTEM_PROMPT
            if chapter_context:
                system += f"\n\nCurrent topic context:\n{chapter_context}"
            system += _adaptive_addon(subject, chapter_title)

            client = _get_gemini_client(key)
            config = _gemini_config(system)
            if client and config:
                from google.genai import types

                chat_history = []
                if history:
                    for h in history[-6:]:
                        role = h.get("role", "user")
                        content = h.get("message", "")
                        if not content:
                            continue
                        gemini_role = "user" if role == "user" else "model"
                        chat_history.append(
                            types.Content(role=gemini_role, parts=[types.Part(text=content)])
                        )

                chat = client.chats.create(
                    model=GEMINI_MODEL,
                    config=config,
                    history=chat_history,
                )
                response = chat.send_message(question)
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    return text, True
        except Exception:
            pass

    return _builtin_response(question, subject, chapter_context), False


def _builtin_response(question, subject, context):
    """Generate a helpful response without Gemini using built-in knowledge."""
    SYLLABUS = get_syllabus()         # 🧠 Live curriculum (Phase 4)
    q_lower = question.lower().strip()

    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    if any(q_lower.startswith(g) for g in greetings):
        return (
            "Hello there! 👋 I'm your AI Tutor! I'm here to help you learn and grow. "
            "Which subject do you want to explore today? 📚\n\n"
            "You can ask me about:\n"
            "- 📖 English, Bengali, Hindi\n"
            "- 🔢 Mathematics\n"
            "- 🔬 Biology, Physics, Chemistry\n"
            "- 🌍 History, Geography\n"
            "- 💻 Computer Studies, AI & Robotics\n\n"
            "Just ask me anything! 😊"
        )

    subj_data = SYLLABUS.get(subject, {})
    chapters = subj_data.get("chapters", [])

    best_chapter = None
    best_score = 0
    for chapter in chapters:
        title_words = set(chapter["title"].lower().split())
        topic_words = set(" ".join(chapter.get("topics", [])).lower().split())
        all_words = title_words | topic_words
        q_words = set(q_lower.split())
        score = len(q_words & all_words)
        if score > best_score:
            best_score = score
            best_chapter = chapter

    if best_chapter and best_score > 0:
        response = f"Great question about **{best_chapter['title']}**! 🌟\n\n"
        response += f"{best_chapter['explanation']}\n\n"
        if best_chapter.get("key_points"):
            response += "**Key Points to Remember:**\n"
            for kp in best_chapter["key_points"][:4]:
                response += f"• {kp}\n"
        if best_chapter.get("examples"):
            response += f"\n**Example:** {best_chapter['examples'][0]}"
        response += "\n\n💡 *Tip: Open this chapter in the Learn section for complete notes and practice questions!*"
        return response

    if any(w in q_lower for w in ["what is", "what are", "define", "meaning of"]):
        return (
            f"That's a thoughtful question! 🤔\n\n"
            f"I'm working with built-in knowledge right now. For a detailed explanation, "
            f"please add your **Gemini API key** in ⚙️ Settings — then I can answer "
            f"any question with full AI power!\n\n"
            f"Meanwhile, try the **Learn** section for {get_subject(subject)['name']} "
            f"chapters with complete explanations. 📚"
        )

    if any(w in q_lower for w in ["solve", "calculate", "find", "how much", "how many"]):
        return (
            "Let me help you solve this step by step! 🔢\n\n"
            "For mathematics problems, I need my full AI brain (Gemini API key).\n\n"
            "**Tips for solving:**\n"
            "1. Read the problem carefully\n"
            "2. Identify what is given and what to find\n"
            "3. Choose the right formula\n"
            "4. Work step by step\n"
            "5. Check your answer\n\n"
            "Try the **Practice** section for guided practice questions with answers! 📝"
        )

    if any(w in q_lower for w in ["why", "how does", "explain"]):
        return (
            "Excellent curiosity! 🌟 Asking 'why' is the sign of a great student!\n\n"
            "For detailed explanations, add your Gemini API key in Settings.\n\n"
            "In the meantime, check the **Learn** section - each chapter has:\n"
            "✅ Simple explanations\n"
            "✅ Real-life examples\n"
            "✅ Key points to remember\n"
            "✅ Practice questions\n\n"
            "Keep that curiosity alive! 🚀"
        )

    return (
        f"I received your question! 😊\n\n"
        f"**To unlock full AI power:**\n"
        f"1. Go to ⚙️ Settings\n"
        f"2. Enter your Gemini API key (starts with AIza...)\n"
        f"3. Come back and ask anything!\n\n"
        f"**Right now you can:**\n"
        f"📖 Learn from the Learn section\n"
        f"📝 Practice with quizzes\n"
        f"🎮 Play brain games\n"
        f"📊 Track your progress\n\n"
        f"Keep studying - you're doing great! 🏆"
    )


def _gemini_generate(api_key, system_prompt, user_prompt):
    """Single-turn generation helper. Returns text or None on failure."""
    client = _get_gemini_client(api_key)
    config = _gemini_config(system_prompt)
    if not client or not config:
        return None
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            config=config,
            contents=user_prompt,
        )
        text = (getattr(response, "text", None) or "").strip()
        return text or None
    except Exception:
        return None


def generate_questions(subject, chapter, difficulty="Medium", count=5, api_key="",
                       uploaded_content=""):
    """Generate practice questions. Returns list of {question, answer, type, ...}.

    If `difficulty == 'Adaptive'`, we look up the Adaptive Engine profile
    for (subject, chapter) and use its current level."""
    # Adaptive: resolve to a concrete level
    if difficulty == "Adaptive":
        try:
            from modules.adaptive_engine import get_profile
            difficulty = get_profile(subject, chapter)["current_level"]
        except Exception:
            difficulty = "Medium"

    builtin_questions = _get_builtin_questions(subject, chapter, difficulty, count)

    key = _resolve_api_key(api_key)
    if key:
        context = f"Subject: {subject}, Chapter: {chapter}"
        if uploaded_content:
            context += f"\n\nContent:\n{uploaded_content[:2000]}"

        system = AI_SYSTEM_PROMPT + _adaptive_addon(subject, chapter)
        prompt = f"""Generate {count} practice questions for Class 6 ICSE students.
Subject: {subject}
Chapter/Topic: {chapter}
Difficulty: {difficulty}
{context}

Return ONLY a numbered list in this format:
1. Q: [question]
   A: [answer]

Make questions appropriate for 11-year-old students."""

        text = _gemini_generate(key, system, prompt)
        if text:
            ai_questions = _parse_qa_text(text)
            if ai_questions:
                return ai_questions[:count]

    return builtin_questions[:count]


def _get_builtin_questions(subject, chapter, difficulty, count):
    SYLLABUS = get_syllabus()         # 🧠 Live curriculum (Phase 4)
    subj_data = SYLLABUS.get(subject, {})
    chapters = subj_data.get("chapters", [])

    matching_chapter = None
    for ch in chapters:
        if (chapter.lower() in ch["title"].lower() or
                ch["title"].lower() in chapter.lower() or
                str(ch.get("id")) == str(chapter)):
            matching_chapter = ch
            break

    if not matching_chapter and chapters:
        matching_chapter = random.choice(chapters)

    if not matching_chapter:
        return _generate_generic_questions(subject, chapter, difficulty, count)

    questions = matching_chapter.get("questions", [])

    if difficulty == "Easy" and len(questions) > 2:
        questions = questions[:max(2, len(questions)//2)]
    elif difficulty == "Hard" and len(questions) > 2:
        questions = questions[len(questions)//2:]

    result = []
    for q in questions:
        result.append({
            "question": q["q"],
            "answer": q["a"],
            "type": q.get("type", "short"),
            "options": q.get("options", []),
            "subject": subject,
            "chapter": matching_chapter["title"],
            "difficulty": difficulty
        })

    random.shuffle(result)

    while len(result) < count:
        result.extend(_generate_generic_questions(subject, chapter, difficulty, 2))

    return result[:count]


def _generate_generic_questions(subject, chapter, difficulty, count):
    subj_name = get_subject(subject)["name"]
    templates = [
        {"question": f"Explain the main concept of {chapter} in {subj_name}.",
         "answer": f"This is about {chapter} in {subj_name}. Study this topic in your textbook for the complete answer.",
         "type": "short"},
        {"question": f"What are 3 important points to remember about {chapter}?",
         "answer": f"Review your {subj_name} textbook chapter on {chapter} for key points.",
         "type": "short"},
        {"question": f"Give one real-life example related to {chapter}.",
         "answer": f"Think of an example you've seen in daily life that relates to {chapter}.",
         "type": "short"},
        {"question": f"Why is {chapter} important to learn in {subj_name}?",
         "answer": f"Understanding {chapter} helps us understand the world around us.",
         "type": "short"},
        {"question": f"Write a short note on {chapter} in {subj_name}.",
         "answer": f"Refer to your textbook for a complete note on this topic.",
         "type": "short"},
    ]
    random.shuffle(templates)
    for t in templates:
        t["subject"] = subject
        t["chapter"] = chapter
        t["difficulty"] = difficulty
        t["options"] = []
    return templates[:count]


def _parse_qa_text(text):
    """Parse numbered Q&A text from model response."""
    questions = []
    lines = text.strip().split('\n')
    current_q = None
    current_a = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(('Q:', '   Q:')) or ('Q:' in line and len(line) < 200):
            if current_q and current_a:
                questions.append({"question": current_q, "answer": current_a, "type": "short", "options": []})
            current_q = line.split('Q:', 1)[-1].strip()
            current_a = None
        elif line.startswith(('A:', '   A:')) or ('A:' in line and len(line) < 200):
            current_a = line.split('A:', 1)[-1].strip()
        elif current_q and not current_a and line and not line[0].isdigit():
            if current_q:
                current_q += " " + line

    if current_q and current_a:
        questions.append({"question": current_q, "answer": current_a, "type": "short", "options": []})

    return questions


def solve_homework(problem, subject, api_key=""):
    """Solve a homework problem with step-by-step explanation."""
    key = _resolve_api_key(api_key)
    if key:
        prompt = f"""A Class 6 ICSE student needs help with this {subject} problem:

{problem}

Please:
1. Understand the problem
2. Identify what is given and what to find
3. Show step-by-step solution
4. Give the final answer clearly
5. Explain WHY each step is done (help student understand, not just copy)

Use simple language for an 11-year-old. Use emojis to make it friendly."""
        text = _gemini_generate(key, AI_SYSTEM_PROMPT, prompt)
        if text:
            return text

    return _builtin_homework_solver(problem, subject)


def _builtin_homework_solver(problem, subject):
    return (
        f"Let me help you with this problem! 🎯\n\n"
        f"**Steps to solve any {subject} problem:**\n\n"
        f"**Step 1: Read Carefully 📖**\n"
        f"Read the problem at least twice. What is being asked?\n\n"
        f"**Step 2: Identify Given Information 📝**\n"
        f"Write down what information you already have.\n\n"
        f"**Step 3: Choose the Right Method 🔧**\n"
        f"Which formula or concept from your textbook applies here?\n\n"
        f"**Step 4: Solve Step by Step 🔢**\n"
        f"Work through the problem one step at a time.\n\n"
        f"**Step 5: Check Your Answer ✅**\n"
        f"Does your answer make sense? Re-read the question.\n\n"
        f"💡 **For complete AI-powered homework help:**\n"
        f"Add your Gemini API key in Settings to get step-by-step solutions for any problem!\n\n"
        f"📚 Also check the relevant chapter in the Learn section for formulas and examples."
    )


# ─────────────────────────────────────────────────────────
# IMAGE DOUBT SOLVER (Gemini Vision — no OCR needed)
# ─────────────────────────────────────────────────────────

def solve_image_doubt(image_bytes: bytes, mime_type: str = "image/jpeg",
                      subject: str = "general", extra_note: str = "",
                      api_key: str = ""):
    """
    Solve a doubt from an uploaded image (math problem, textbook excerpt, etc.).
    Gemini 2.5 reads the image directly — no OCR step needed.

    Returns (response_text: str, used_ai: bool).
    """
    key = _resolve_api_key(api_key)
    if not key:
        return (
            "📸 **Image received!**\n\n"
            "I need a Gemini API key to read images. Please add one in ⚙️ Settings → AI Settings.\n\n"
            "Tip: meanwhile, type your question in **Ask AI Tutor** and I'll explain step-by-step.",
            False,
        )

    if not image_bytes:
        return ("Please upload an image first.", False)

    client = _get_gemini_client(key)
    config = _gemini_config(AI_SYSTEM_PROMPT)
    if not client or not config:
        return (
            "Could not start the AI client. Please check your Gemini API key.",
            False,
        )

    subj_name = (get_subject(subject)["name"]
                 if subject and subject != "general" else "any subject")

    note_block = f"\n\nAdditional note from the student:\n{extra_note.strip()}" if extra_note.strip() else ""

    user_prompt = f"""A Class 6 ICSE student has uploaded a photo of a question they need help with.
Subject hint: {subj_name}.{note_block}

Please:
1. First, in ONE line, restate what the question is asking (so the child knows you understood it).
2. Then solve it **step by step**, one step per line, in very simple language.
3. Mark the final answer clearly with **Final Answer:**
4. End with one short follow-up question.

If the image is unclear or has no question, say so kindly and ask the child to retake the photo with better light."""

    try:
        from google.genai import types
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            config=config,
            contents=[image_part, user_prompt],
        )
        text = (getattr(response, "text", None) or "").strip()
        if text:
            return text, True
        return ("Hmm, I couldn't read that image clearly. Try a sharper photo with good light.", False)
    except Exception as e:
        return (
            f"Sorry — I had trouble reading that image. ({type(e).__name__})\n\n"
            "Please try again with a clearer, brighter photo of just the question.",
            False,
        )


def analyze_exam_paper(extracted_text, api_key=""):
    """Analyze an uploaded exam paper and identify weak areas."""
    key = _resolve_api_key(api_key)
    if key:
        prompt = f"""Analyze this Class 6 ICSE exam paper/answer sheet:

{extracted_text[:3000]}

Please provide:
1. Topics covered in the paper
2. Difficulty level assessment
3. Types of questions (MCQ, short answer, long answer)
4. Key topics the student should revise
5. Predicted similar questions for practice

Format clearly with headings and bullet points."""
        text = _gemini_generate(key, AI_SYSTEM_PROMPT, prompt)
        if text:
            return text

    return (
        "📄 **Exam Paper Analysis**\n\n"
        "Your paper has been uploaded successfully!\n\n"
        "To get AI-powered analysis (weak areas, predicted questions, revision tips),\n"
        "please add your Gemini API key in Settings.\n\n"
        "**Manual Review Tips:**\n"
        "• Check which questions you got wrong\n"
        "• Revise those topics in the Learn section\n"
        "• Practice similar questions in the Practice section"
    )
