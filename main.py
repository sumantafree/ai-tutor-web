"""
AI Home Tutor - Main Application
Class 6 ICSE Board | Child-Friendly AI-Powered Tutor

Run with: streamlit run main.py
"""

import streamlit as st
import sys
import os

# ── Add project root to path ─────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Load environment variables from .env (local dev only) ─
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

# ── Page configuration (MUST be first Streamlit call) ────
st.set_page_config(
    page_title="🎓 AI Home Tutor - Class 6 ICSE",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AI Home Tutor for Class 6 ICSE | Made with ❤️ for students"
    }
)

# ── Initialize database ──────────────────────────────────
from utils.database import init_database
from utils.helpers import ensure_data_dirs
init_database()
ensure_data_dirs()

# ── Import modules AFTER path setup ──────────────────────
from utils.config import APP_TITLE, get_subject
import utils.database as db

# ────────────────────────────────────────────────────────────────────────────
# CSS - Child-Friendly, Colorful Design
# ────────────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    /* ── Global Fonts & Colors ── */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', 'Segoe UI', sans-serif !important;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* ── Sidebar nav buttons (override the global light button style) ── */
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background-color: rgba(255,255,255,0.06) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        text-align: left !important;
        padding: 0.55rem 0.9rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button p,
    [data-testid="stSidebar"] [data-testid="stButton"] button span,
    [data-testid="stSidebar"] [data-testid="stButton"] button div {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background-color: rgba(74,144,226,0.55) !important;   /* #4A90E2 hover */
        border-color: rgba(74,144,226,0.9) !important;
        color: #FFFFFF !important;
    }

    /* Active page (Streamlit applies type="primary") */
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #6C5CE7, #4A90E2) !important;
        border-color: #6C5CE7 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }

    /* ── Page Title ── */
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #2d3436;
        margin-bottom: 1.5rem;
        padding: 0.5rem 0;
        border-bottom: 3px solid #6C5CE7;
    }

    /* ── Home Banner ── */
    .home-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .banner-left {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .avatar-large {
        font-size: 4rem;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .greeting-text {
        font-size: 1.8rem;
        font-weight: 800;
    }

    .date-text {
        font-size: 1rem;
        opacity: 0.85;
        margin-top: 0.2rem;
    }

    .motivation {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-style: italic;
    }

    /* ── Stat Cards ── */
    .stat-card {
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }

    .stat-card:hover { transform: translateY(-3px); }
    .stat-blue   { background: linear-gradient(135deg, #74B9FF, #0984e3); color: white; }
    .stat-orange { background: linear-gradient(135deg, #fd79a8, #e84393); color: white; }
    .stat-green  { background: linear-gradient(135deg, #55efc4, #00b894); color: white; }
    .stat-purple { background: linear-gradient(135deg, #a29bfe, #6c5ce7); color: white; }

    .stat-icon  { font-size: 2rem; }
    .stat-value { font-size: 1.8rem; font-weight: 800; }
    .stat-label { font-size: 0.85rem; opacity: 0.9; }

    /* ── Section Title ── */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3436;
        margin: 1rem 0 0.7rem;
    }

    /* ── Subject Buttons (via Streamlit buttons, custom CSS on containers) ── */
    [data-testid="stButton"] button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: 1px solid #dee2e6 !important;
        background-color: #f8f9fa !important;
        transition: all 0.2s !important;
    }

    [data-testid="stButton"] button:hover {
        background-color: #e9ecef !important;
        border-color: #adb5bd !important;
        transform: translateY(-1px);
    }

    /* ── Badge Container ── */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 0.5rem 0;
    }

    .badge-item {
        text-align: center;
        background: #fff8e5;
        border: 2px solid #FDCB6E;
        border-radius: 12px;
        padding: 0.7rem;
        width: 80px;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .badge-item:hover { transform: scale(1.1); }
    .badge-name { font-size: 0.7rem; font-weight: 600; color: #636e72; margin-top: 0.3rem; }

    .badge-display {
        text-align: center;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }

    .badge-display.earned {
        background: #fff8e5;
        border: 2px solid #FDCB6E;
    }

    .badge-display.locked {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
    }

    .badge-icon-large { font-size: 2.5rem; }
    .badge-name-display { font-weight: 700; font-size: 0.85rem; margin-top: 0.5rem; }
    .badge-date { font-size: 0.75rem; color: #aaa; }

    /* ── Chapter Header ── */
    .chapter-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
    }

    .chapter-title { font-size: 1rem; font-weight: 600; color: #636e72; }
    .chapter-subtitle { font-size: 1.5rem; font-weight: 800; color: #2d3436; }

    .completed-badge {
        background: #00b894;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    /* ── Topic Pills ── */
    .topics-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0; }

    .topic-pill {
        background: #f0f0ff;
        color: #6c5ce7;
        border: 1px solid #a29bfe;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* ── Explanation Box ── */
    .explanation-box {
        background: #f8f9ff;
        border-radius: 12px;
        padding: 1.5rem;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #2d3436;
        margin: 0.5rem 0;
    }

    /* ── Key Point ── */
    .key-point-item {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        background: #fafafa;
        border-radius: 10px;
    }

    .kp-number {
        background: #6c5ce7;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
        flex-shrink: 0;
        min-width: 28px;
    }

    .kp-text { font-size: 0.95rem; line-height: 1.5; padding-top: 2px; }

    /* ── Example Box ── */
    .example-box {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.7rem 0;
    }

    .example-num { font-size: 0.8rem; font-weight: 700; color: #636e72; text-transform: uppercase; }
    .example-text { font-size: 1rem; margin: 0.3rem 0 0; line-height: 1.6; }

    /* ── Summary Box ── */
    .summary-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        max-height: 400px;
        overflow-y: auto;
    }

    /* ── Quiz Card ── */
    .quiz-header {
        background: #f8f9ff;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0 1rem;
        display: flex;
        gap: 1.5rem;
        font-size: 0.9rem;
        flex-wrap: wrap;
    }

    .question-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0 0.3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    .question-number { font-size: 0.8rem; font-weight: 700; color: #6c5ce7; text-transform: uppercase; }
    .question-text { font-size: 1.05rem; font-weight: 600; color: #2d3436; margin-top: 0.4rem; }

    /* ── Results Banner ── */
    .results-banner {
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }

    .results-score { font-size: 4rem; font-weight: 800; }
    .results-grade { font-size: 1.5rem; margin: 0.5rem 0; }
    .results-detail { font-size: 1rem; opacity: 0.8; }

    /* ── Quiz History Item ── */
    .quiz-history-item {
        display: flex;
        gap: 1.5rem;
        align-items: center;
        padding: 0.6rem 1rem;
        background: white;
        border-radius: 8px;
        margin: 0.3rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        flex-wrap: wrap;
    }

    /* ── Game Boxes ── */
    .game-score-bar {
        display: flex;
        gap: 2rem;
        background: #f0f0ff;
        border-radius: 10px;
        padding: 0.7rem 1.2rem;
        margin: 0.5rem 0 1rem;
        font-weight: 600;
        font-size: 1rem;
        flex-wrap: wrap;
    }

    .puzzle-box {
        background: linear-gradient(135deg, #f8f9ff, #e8e8ff);
        border: 2px solid #a29bfe;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .puzzle-icon { font-size: 3rem; margin-bottom: 1rem; }
    .puzzle-question { font-size: 1.2rem; font-weight: 700; color: #2d3436; line-height: 1.5; }

    .scramble-box {
        background: linear-gradient(135deg, #fff5f5, #ffe8e8);
        border: 2px solid #fd79a8;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .scramble-label { font-size: 0.9rem; color: #636e72; font-weight: 600; }
    .scrambled-word {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e84393;
        letter-spacing: 0.3rem;
        margin: 1rem 0;
        font-family: monospace;
    }

    .scramble-hint { color: #636e72; font-size: 0.95rem; margin: 0.5rem 0; }
    .scramble-info { color: #aaa; font-size: 0.85rem; }

    .pattern-box {
        background: linear-gradient(135deg, #f0fff4, #e8ffe8);
        border: 2px solid #55efc4;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .pattern-sequence {
        font-size: 2rem;
        font-weight: 800;
        color: #00b894;
        margin: 1rem 0;
        letter-spacing: 0.2rem;
    }

    .pattern-question { color: #636e72; font-size: 1rem; }

    .vocab-box {
        background: linear-gradient(135deg, #fff8e5, #ffe8c0);
        border: 2px solid #FDCB6E;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .vocab-question { font-size: 1.3rem; font-weight: 700; color: #2d3436; }

    .logic-box {
        background: linear-gradient(135deg, #f0f8ff, #e0f0ff);
        border: 2px solid #74B9FF;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .logic-question { font-size: 1.2rem; font-weight: 700; color: #2d3436; line-height: 1.5; }

    /* ── Memory Match ── */
    .mm-card {
        border-radius: 10px;
        padding: 1rem 0.5rem;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .mm-matched {
        background: #d4edda;
        border: 2px solid #28a745;
        color: #155724;
    }

    .mm-flipped {
        background: #cce5ff;
        border: 2px solid #004085;
        color: #004085;
    }

    /* ── Chat ── */
    .chat-user {
        display: flex;
        justify-content: flex-end;
        align-items: flex-start;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .chat-assistant {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 0.8rem 1.2rem;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    .chat-bubble-ai {
        background: #f1f3f4;
        color: #2d3436;
        border-radius: 18px 18px 18px 4px;
        padding: 0.8rem 1.2rem;
        max-width: 75%;
        font-size: 0.95rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    .chat-avatar-user, .chat-avatar-ai {
        font-size: 1.5rem;
        flex-shrink: 0;
        padding-top: 4px;
    }

    /* ── Solution Box ── */
    .solution-box {
        background: #f8fff8;
        border: 2px solid #00b894;
        border-radius: 12px;
        padding: 1.5rem;
        font-size: 1rem;
        line-height: 1.7;
        white-space: pre-wrap;
    }

    /* ── Rapid Fire ── */
    .rapid-question {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .rapid-num { font-size: 1rem; color: #FDCB6E; font-weight: 700; margin-bottom: 0.5rem; }
    .rapid-q-text { font-size: 1.3rem; font-weight: 700; line-height: 1.5; }

    .rapid-results {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 1rem 0;
    }

    /* ── Upload Banner ── */
    .upload-banner {
        background: linear-gradient(135deg, #74B9FF22, #0984e322);
        border: 1px solid #74B9FF;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #2d3436;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }

    /* ── Games Banner ── */
    .games-banner {
        background: linear-gradient(135deg, #fd79a822, #e8439322);
        border: 1px solid #fd79a8;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #2d3436;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* ── Tip Card ── */
    .tip-card {
        background: #f8f9ff;
        border-left: 3px solid #6c5ce7;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* ── Parent Card ── */
    .parent-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }

    /* ── Level Display ── */
    .level-display {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
    }

    .level-icon { font-size: 3rem; }
    .level-name { font-size: 1.5rem; font-weight: 800; }
    .level-points { font-size: 1rem; opacity: 0.8; }
    .level-next { font-size: 0.85rem; opacity: 0.6; margin-top: 0.3rem; }

    /* ── Sidebar App Title ── */
    .app-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: white;
        padding: 0.5rem 0 1rem;
        text-align: center;
        letter-spacing: 0.5px;
    }

    .app-subtitle {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* ── Hide Streamlit default elements ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Streamlit specific overrides ── */
    .stSelectbox label { font-weight: 600; }
    .stTextInput label { font-weight: 600; }
    .stTextArea label { font-weight: 600; }
    .stSlider label { font-weight: 600; }

    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ────────────────────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "page": "home",
        "selected_subject": None,
        "voice_enabled": False,
        "quiz_active": False,
        "quiz_questions": [],
        "quiz_answers": [],
        "quiz_submitted": False,
        "test_active": False,
        "rapid_active": False,
        "current_game": None,
        "game_state": {},
        "chat_messages": [],
        "chat_subject": "general",
        "chat_context": "",
        "settings_open": False,
        "voice_input_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # App title
        st.markdown("""
        <div class="app-title">🎓 AI Home Tutor</div>
        <div class="app-subtitle">Class 6 ICSE Board</div>
        """, unsafe_allow_html=True)

        # Student info
        student = db.get_student()
        name = student.get("name", "Student")
        avatar = student.get("avatar", "🎓")
        points = db.get_total_points()
        streak = db.get_current_streak()

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); border-radius:12px; padding:0.8rem; margin-bottom:1rem; text-align:center;">
            <div style="font-size:2.5rem">{avatar}</div>
            <div style="font-weight:700; font-size:1.1rem">{name}</div>
            <div style="opacity:0.8; font-size:0.85rem">⭐ {points} pts | 🔥 {streak} days</div>
        </div>
        """, unsafe_allow_html=True)

        # Main navigation
        nav_pages = [
            ("🏠", "Home",              "home"),
            ("📖", "Learn",             "learn"),
            ("📝", "Practice",          "practice"),
            ("🎮", "Play Games",        "play"),
            ("🤖", "Ask AI Tutor",      "chat"),
            ("📸", "Doubt Solver",      "doubt_solver"),
            ("📊", "Progress",          "progress"),
            ("📤", "Upload Materials",  "upload"),
            ("📅", "Study Planner",     "planner"),
            ("📚", "Curriculum",        "admin_curriculum"),
            ("⚙️", "Settings",         "settings"),
        ]

        for icon, label, page in nav_pages:
            current = st.session_state.page == page
            btn_type = "primary" if current else "secondary"

            # Use unique keys
            if st.button(f"{icon} {label}", key=f"nav_sidebar_{page}",
                         use_container_width=True,
                         type=btn_type):
                st.session_state.page = page
                # Reset game state when navigating away from play
                if page != "play":
                    st.session_state.current_game = None
                st.rerun()

        # Daily reminder
        st.markdown("---")
        from utils.helpers import get_motivation
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); border-radius:8px; padding:0.8rem;
                    font-size:0.8rem; text-align:center; font-style:italic;">
            {get_motivation()}
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# SETTINGS PAGE
# ────────────────────────────────────────────────────────────────────────────

def render_settings():
    """Settings page for parent to configure the app."""
    st.markdown('<div class="page-title">⚙️ Settings</div>', unsafe_allow_html=True)

    student = db.get_student()

    tab1, tab2, tab3 = st.tabs(["👤 Student Profile", "🤖 AI Settings", "🔊 Voice Settings"])

    with tab1:
        st.markdown("### 👤 Student Profile")

        name = st.text_input("Student Name", value=student.get("name", "Student"), key="set_name")
        age = st.number_input("Age", min_value=8, max_value=16, value=student.get("age", 11), key="set_age")

        avatars = ["🎓", "⭐", "🚀", "🦁", "🦊", "🐯", "🦅", "🌟", "💫", "🏆"]
        current_avatar = student.get("avatar", "🎓")
        cols = st.columns(len(avatars))
        for i, (col, av) in enumerate(zip(cols, avatars)):
            with col:
                if st.button(av, key=f"av_{i}",
                             type="primary" if av == current_avatar else "secondary"):
                    db.update_student(avatar=av)
                    st.rerun()

        if st.button("💾 Save Profile", use_container_width=True, key="save_profile"):
            db.update_student(name=name, age=age)
            st.success("✅ Profile saved!")
            st.rerun()

    with tab2:
        st.markdown("### 🤖 AI Settings (Google Gemini)")
        import os as _os
        env_key_set = bool(_os.environ.get("GEMINI_API_KEY", "").strip())
        if env_key_set:
            st.success("✅ A Gemini API key is configured on the server (GEMINI_API_KEY env var). Full AI mode is ON for all sessions.")

        st.info(
            "🔑 **How to get a Gemini API Key:**\n"
            "1. Go to aistudio.google.com/app/apikey\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Create API key'\n"
            "4. Copy and paste it below (starts with 'AIza...')\n\n"
            "Without an API key, the tutor works in Basic Mode with built-in content."
        )

        current_key = student.get("api_key", "") or ""
        masked_key = f"AIza...{current_key[-6:]}" if len(current_key) > 10 else ""

        new_key = st.text_input(
            "Gemini API Key",
            value="",
            type="password",
            placeholder=masked_key if masked_key else "AIza...",
            key="set_api_key",
            help="Your API key is stored in the database and never shared."
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save API Key", key="save_api", use_container_width=True):
                from modules.ai_engine import is_valid_gemini_key
                if is_valid_gemini_key(new_key):
                    db.update_student(api_key=new_key.strip())
                    st.success("✅ API key saved! Full Gemini AI mode activated!")
                    st.rerun()
                elif new_key.strip():
                    st.error("❌ Invalid API key format. Gemini keys start with 'AIza' and are 30+ chars.")

        with col2:
            if current_key and st.button("🗑️ Remove API Key", key="remove_api", use_container_width=True):
                db.update_student(api_key="")
                st.success("API key removed.")
                st.rerun()

        if current_key and current_key.startswith("AIza"):
            st.success("✅ Gemini API key is configured - Full AI mode is ON!")

    with tab3:
        st.markdown("### 🔊 Voice Settings (Browser-native — free, no APIs)")
        from modules.browser_voice import (
            render_capabilities_probe, render_test_voice_button,
            LANG_LABELS, LANG_CODES,
        )

        st.caption(
            "Voice runs **inside your browser** using the Web Speech API. "
            "Best in Google Chrome or Microsoft Edge. The first time, your browser "
            "will ask for microphone permission — please tap **Allow**."
        )

        st.markdown("#### Browser capabilities (this device)")
        render_capabilities_probe()

        st.markdown("#### Preferences")
        col_a, col_b = st.columns(2)
        with col_a:
            voice_on = st.toggle(
                "🔊 Speak AI replies aloud",
                value=st.session_state.get("voice_enabled", True),
                key="settings_voice_toggle",
            )
            st.session_state.voice_enabled = voice_on
        with col_b:
            cur_lang = st.session_state.get("voice_lang", "en-IN")
            lang_idx = LANG_CODES.index(cur_lang) if cur_lang in LANG_CODES else 0
            lang_label = st.selectbox(
                "🌐 Voice language",
                LANG_LABELS,
                index=lang_idx,
                key="settings_lang_sel",
            )
            st.session_state.voice_lang = LANG_CODES[LANG_LABELS.index(lang_label)]

        render_test_voice_button(
            lang=st.session_state.get("voice_lang", "en-IN"),
            key="settings_test_voice",
        )

        with st.expander("Why don't I see my old microphone permissions?"):
            st.markdown(
                "- Voice now runs in **your browser**, not on the server, so it works "
                "for free with no API keys and no installs.\n"
                "- If the mic doesn't pop up: open the lock 🔒 icon in the address bar → "
                "set Microphone to **Allow** for this site.\n"
                "- Firefox doesn't support browser speech recognition — use Chrome, Edge, "
                "or Brave for the mic. Speech output (the AI talking back) works "
                "everywhere."
            )

        st.markdown("---")
        st.markdown("### 🗄️ Data Management")
        if st.button("🗑️ Reset All Progress (Use with caution!)", key="reset_all",
                     type="secondary", use_container_width=True):
            st.session_state["_show_reset_confirm"] = True

        if st.session_state.get("_show_reset_confirm"):
            st.warning("⚠️ This will permanently delete ALL progress, quiz history, and points!")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Yes, Reset Everything", key="confirm_reset_yes",
                             use_container_width=True, type="primary"):
                    from utils.database import get_connection, _exec
                    conn = get_connection()
                    for table in ["study_sessions", "quiz_results", "question_history",
                                  "badges", "streaks", "chat_history", "uploaded_content",
                                  "study_plan", "game_scores", "chapter_progress"]:
                        _exec(conn, f"DELETE FROM {table}")
                    _exec(conn, "UPDATE points SET total_points=0, today_points=0, last_updated='' WHERE id=1")
                    conn.commit()
                    conn.close()
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.success("All data reset! Refreshing...")
                    st.rerun()
            with col_no:
                if st.button("❌ Cancel", key="confirm_reset_no", use_container_width=True):
                    st.session_state["_show_reset_confirm"] = False
                    st.rerun()


# ────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ────────────────────────────────────────────────────────────────────────────

def main():
    inject_css()
    init_session_state()
    render_sidebar()

    page = st.session_state.get("page", "home")

    # Page routing
    if page == "home":
        from ui.home import render_home
        render_home()

    elif page == "learn":
        from ui.learn import render_learn
        render_learn()

    elif page == "practice":
        from ui.practice import render_practice
        render_practice()

    elif page == "play":
        from ui.play import render_play
        render_play()

    elif page == "chat":
        from ui.chat import render_chat
        render_chat()

    elif page == "doubt_solver":
        from ui.doubt_solver import render_doubt_solver
        render_doubt_solver()

    elif page == "admin_curriculum":
        from ui.admin_curriculum import render_admin_curriculum
        render_admin_curriculum()

    elif page == "progress":
        from ui.progress import render_progress
        render_progress()

    elif page == "upload":
        from ui.upload import render_upload
        render_upload()

    elif page == "planner":
        from ui.planner import render_planner
        render_planner()

    elif page == "settings":
        render_settings()

    else:
        from ui.home import render_home
        render_home()


if __name__ == "__main__":
    main()
