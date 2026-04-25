"""
Play Page UI - Brain development games
"""

import streamlit as st
import time
import random
from modules.game_engine import (
    get_memory_game_cards, get_math_puzzle, get_word_scramble,
    get_pattern_puzzle, get_vocab_question, get_logic_puzzle,
    GAMES_CATALOG, MEMORY_SETS, WORD_LISTS
)
import utils.database as db
from utils.helpers import get_grade_emoji


def render_play():
    """Render the games page."""
    st.markdown('<div class="page-title">🎮 Brain Games</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="games-banner">
        🧠 Play games to grow your brain! Each game earns you points and badges!
    </div>
    """, unsafe_allow_html=True)

    # High scores
    high_scores = db.get_game_high_scores()

    # Game selection
    current_game = st.session_state.get("current_game", None)

    if not current_game:
        _show_game_catalog(high_scores)
    else:
        _run_game(current_game)


def _show_game_catalog(high_scores):
    """Show the game selection grid."""
    from modules.game_engine import GAMES_CATALOG

    st.markdown("### 🎮 Choose Your Game")

    cols = st.columns(3)
    for i, game in enumerate(GAMES_CATALOG):
        col = cols[i % 3]
        with col:
            hs = high_scores.get(game["name"], {}).get("high_score", 0)
            plays = high_scores.get(game["name"], {}).get("plays", 0)

            hs_text = f"🏆 Best: {hs}" if hs > 0 else "🎯 Not played yet"
            plays_text = f"🎮 {plays} plays" if plays > 0 else ""

            if st.button(
                f"{game['icon']}\n**{game['name']}**\n{game['desc']}\n{hs_text}",
                key=f"game_{game['id']}",
                use_container_width=True,
                help=game["desc"]
            ):
                st.session_state.current_game = game["id"]
                st.session_state.game_state = {}
                st.rerun()


def _run_game(game_id):
    """Route to the correct game."""
    # Back button
    if st.button("⬅️ Back to Games", key="back_games"):
        st.session_state.current_game = None
        st.session_state.game_state = {}
        st.rerun()

    st.markdown("---")

    if game_id == "math_puzzle":
        _game_math_puzzle()
    elif game_id == "word_scramble":
        _game_word_scramble()
    elif game_id == "pattern_game":
        _game_pattern()
    elif game_id == "vocab_game":
        _game_vocabulary()
    elif game_id == "logic_puzzle":
        _game_logic_puzzle()
    elif game_id == "memory_match":
        _game_memory_match()
    elif game_id == "rapid_fire":
        st.info("⚡ Go to the **Practice** tab for the Rapid Fire Quiz!")
    else:
        st.info("Game coming soon!")


# ─────────────────────────────────────────────────────────
# MATH PUZZLE GAME
# ─────────────────────────────────────────────────────────

def _game_math_puzzle():
    """Math puzzle game with score tracking."""
    st.markdown("## 🔢 Math Puzzle")

    gs = st.session_state.get("game_state", {})
    score = gs.get("score", 0)
    total = gs.get("total", 0)
    streak = gs.get("streak", 0)

    if "current_puzzle" not in gs or gs.get("show_result"):
        diff = st.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard"], key="mp_diff")
        puzzle = get_math_puzzle(diff)
        gs["current_puzzle"] = puzzle
        gs["show_result"] = False
        gs["user_answer"] = ""
        st.session_state.game_state = gs

    puzzle = gs["current_puzzle"]

    # Score header
    st.markdown(f"""
    <div class="game-score-bar">
        <span>⭐ Score: {score}</span>
        <span>📊 {total} solved</span>
        <span>🔥 Streak: {streak}</span>
        <span>🎯 {puzzle['difficulty']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"""
    <div class="puzzle-box">
        <div class="puzzle-icon">🔢</div>
        <div class="puzzle-question">{puzzle['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if not gs.get("show_result"):
        answer = st.text_input("Your answer:", key=f"mp_ans_{total}", placeholder="Type your answer...")

        if st.button("✅ Submit Answer", key=f"mp_submit_{total}", use_container_width=True):
            from modules.quiz_engine import _check_answer
            is_correct = _check_answer(answer.strip().lower(), puzzle["answer"].strip().lower())
            gs["show_result"] = True
            gs["last_correct"] = is_correct
            gs["user_answer"] = answer
            gs["total"] = total + 1
            if is_correct:
                pts = {"Easy": 10, "Medium": 20, "Hard": 30}.get(puzzle["difficulty"], 20)
                gs["score"] = score + pts
                gs["streak"] = streak + 1
            else:
                gs["streak"] = 0
            st.session_state.game_state = gs
            st.rerun()
    else:
        if gs.get("last_correct"):
            pts = {"Easy": 10, "Medium": 20, "Hard": 30}.get(puzzle["difficulty"], 20)
            st.success(f"🎉 Correct! +{pts} points!")
        else:
            st.error(f"❌ Not quite! The answer was: **{puzzle['answer']}**")
            st.info(f"💡 Explanation: {puzzle.get('explanation', '')}")

        if st.button("➡️ Next Puzzle", key=f"mp_next_{total}", use_container_width=True):
            gs["show_result"] = False
            diff = st.session_state.get("mp_diff", "Medium")
            gs["current_puzzle"] = get_math_puzzle(diff)
            st.session_state.game_state = gs
            if gs["total"] >= 5:
                db.save_game_score("Math Puzzle", gs["score"], diff)
            st.rerun()

        if gs["total"] >= 5:
            if st.button("🏆 Save Score & Exit", key="mp_save", use_container_width=True):
                db.save_game_score("Math Puzzle", gs["score"],
                                   puzzle["difficulty"])
                st.success(f"🏆 Score saved: {gs['score']} points!")
                st.session_state.current_game = None
                st.session_state.game_state = {}
                st.rerun()


# ─────────────────────────────────────────────────────────
# WORD SCRAMBLE GAME
# ─────────────────────────────────────────────────────────

def _game_word_scramble():
    """Word scramble game."""
    st.markdown("## 📝 Word Scramble")
    st.info("Unscramble the letters to form the correct word!")

    gs = st.session_state.get("game_state", {})
    score = gs.get("score", 0)
    total = gs.get("total", 0)
    hints_used = gs.get("hints_used", 0)

    categories = list(WORD_LISTS.keys())
    category = st.selectbox("📚 Category", categories, key="ws_category")

    if "current_word" not in gs or gs.get("show_result") or gs.get("category") != category:
        word_data = get_word_scramble(category)
        gs["current_word"] = word_data
        gs["show_result"] = False
        gs["category"] = category
        st.session_state.game_state = gs

    wd = gs["current_word"]

    st.markdown(f"""
    <div class="game-score-bar">
        <span>⭐ Score: {score}</span>
        <span>📊 {total} solved</span>
    </div>
    """, unsafe_allow_html=True)

    # Scrambled word display
    scrambled_display = " - ".join(list(wd["scrambled"]))
    st.markdown(f"""
    <div class="scramble-box">
        <div class="scramble-label">Unscramble this word:</div>
        <div class="scrambled-word">{scrambled_display}</div>
        <div class="scramble-hint">💡 Hint: {wd['hint']}</div>
        <div class="scramble-info">Letters: {wd['length']} | Category: {wd['category']}</div>
    </div>
    """, unsafe_allow_html=True)

    if not gs.get("show_result"):
        # Show first letter as hint
        if hints_used > 0:
            st.info(f"🔤 First letter: **{wd['word'][0]}**")

        answer = st.text_input("Your answer:", key=f"ws_ans_{total}",
                               placeholder="Type the unscrambled word...",
                               max_chars=30).upper()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit", key=f"ws_submit_{total}", use_container_width=True):
                is_correct = answer.strip() == wd["word"].strip()
                gs["show_result"] = True
                gs["last_correct"] = is_correct
                gs["total"] = total + 1
                if is_correct:
                    pts = max(10, 30 - hints_used * 10)
                    gs["score"] = score + pts
                st.session_state.game_state = gs
                st.rerun()
        with col2:
            if st.button("💡 Use Hint (-10pts)", key=f"ws_hint_{total}", use_container_width=True):
                gs["hints_used"] = hints_used + 1
                st.session_state.game_state = gs
                st.rerun()
    else:
        if gs.get("last_correct"):
            pts = max(10, 30 - hints_used * 10)
            st.success(f"🎉 Correct! The word was **{wd['word']}**! +{pts} points!")
        else:
            st.error(f"❌ The correct word was: **{wd['word']}**")

        if st.button("➡️ Next Word", key=f"ws_next_{total}", use_container_width=True):
            gs["current_word"] = get_word_scramble(category)
            gs["show_result"] = False
            gs["hints_used"] = 0
            st.session_state.game_state = gs
            if gs["total"] >= 5:
                db.save_game_score("Word Scramble", gs["score"], "Medium")
            st.rerun()


# ─────────────────────────────────────────────────────────
# PATTERN GAME
# ─────────────────────────────────────────────────────────

def _game_pattern():
    """Pattern recognition game."""
    st.markdown("## 🔍 Pattern Detective")
    st.info("Find the missing element in the pattern!")

    gs = st.session_state.get("game_state", {})
    score = gs.get("score", 0)
    total = gs.get("total", 0)

    diff = st.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard"], key="pg_diff")

    if "current_pattern" not in gs or gs.get("show_result"):
        gs["current_pattern"] = get_pattern_puzzle(diff)
        gs["show_result"] = False
        st.session_state.game_state = gs

    puzzle = gs["current_pattern"]

    st.markdown(f"""
    <div class="game-score-bar">
        <span>⭐ Score: {score}</span>
        <span>📊 {total} solved</span>
    </div>
    """, unsafe_allow_html=True)

    # Show sequence
    seq_display = " → ".join([str(x) for x in puzzle["sequence"]])
    st.markdown(f"""
    <div class="pattern-box">
        <div class="pattern-sequence">{seq_display}</div>
        <div class="pattern-question">What comes next? (Replace the ❓)</div>
    </div>
    """, unsafe_allow_html=True)

    if not gs.get("show_result"):
        answer = st.text_input("The missing element is:", key=f"pg_ans_{total}",
                               placeholder="Type your answer...")

        if st.button("✅ Submit", key=f"pg_sub_{total}", use_container_width=True):
            from modules.quiz_engine import _check_answer
            is_correct = _check_answer(answer.strip().lower(), str(puzzle["answer"]).lower())
            gs["show_result"] = True
            gs["last_correct"] = is_correct
            gs["total"] = total + 1
            if is_correct:
                pts = {"Easy": 10, "Medium": 20, "Hard": 30}.get(diff, 20)
                gs["score"] = score + pts
            st.session_state.game_state = gs
            st.rerun()
    else:
        if gs.get("last_correct"):
            pts = {"Easy": 10, "Medium": 20, "Hard": 30}.get(diff, 20)
            st.success(f"🎉 Correct! +{pts} points! Pattern rule: *{puzzle['rule']}*")
        else:
            st.error(f"❌ Answer was: **{puzzle['answer']}**")
            st.info(f"💡 Rule: {puzzle['rule']}")

        if st.button("➡️ Next Pattern", key=f"pg_next_{total}", use_container_width=True):
            gs["current_pattern"] = get_pattern_puzzle(diff)
            gs["show_result"] = False
            st.session_state.game_state = gs
            if gs["total"] >= 5:
                db.save_game_score("Pattern Detective", gs["score"], diff)
            st.rerun()


# ─────────────────────────────────────────────────────────
# VOCABULARY GAME
# ─────────────────────────────────────────────────────────

def _game_vocabulary():
    """Vocabulary quiz game."""
    st.markdown("## 📚 Vocabulary Quiz")
    st.info("Choose the correct word for the given meaning!")

    gs = st.session_state.get("game_state", {})
    score = gs.get("score", 0)
    total = gs.get("total", 0)

    if "current_vocab" not in gs or gs.get("show_result"):
        gs["current_vocab"] = get_vocab_question()
        gs["show_result"] = False
        gs["selected"] = None
        st.session_state.game_state = gs

    vq = gs["current_vocab"]

    st.markdown(f"""
    <div class="game-score-bar">
        <span>⭐ Score: {score}</span>
        <span>📊 {total} answered</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vocab-box">
        <div class="vocab-question">{vq['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if not gs.get("show_result"):
        selected = st.radio("Choose:", vq["options"], key=f"vq_{total}")

        if st.button("✅ Submit", key=f"vq_sub_{total}", use_container_width=True):
            is_correct = selected == vq["answer"]
            gs["show_result"] = True
            gs["last_correct"] = is_correct
            gs["selected"] = selected
            gs["total"] = total + 1
            if is_correct:
                gs["score"] = score + 15
            st.session_state.game_state = gs
            st.rerun()
    else:
        if gs.get("last_correct"):
            st.success(f"🎉 Correct! **{vq['answer']}** means '{vq['meaning']}'. +15 points!")
        else:
            st.error(f"❌ You chose **{gs.get('selected')}**. Correct answer: **{vq['answer']}**")
            st.info(f"💡 {vq['answer']} means: {vq['meaning']}")

        if st.button("➡️ Next Word", key=f"vq_next_{total}", use_container_width=True):
            gs["current_vocab"] = get_vocab_question()
            gs["show_result"] = False
            st.session_state.game_state = gs
            if gs["total"] >= 5:
                db.save_game_score("Vocabulary Quiz", gs["score"], "Medium")
            st.rerun()


# ─────────────────────────────────────────────────────────
# LOGIC PUZZLE GAME
# ─────────────────────────────────────────────────────────

def _game_logic_puzzle():
    """Logic puzzles and brain teasers."""
    st.markdown("## 💡 Brain Teaser")
    st.info("Think carefully before answering these logic puzzles!")

    gs = st.session_state.get("game_state", {})
    score = gs.get("score", 0)
    total = gs.get("total", 0)

    if "current_logic" not in gs or gs.get("show_result"):
        gs["current_logic"] = get_logic_puzzle()
        gs["show_result"] = False
        st.session_state.game_state = gs

    puzzle = gs["current_logic"]

    st.markdown(f"""
    <div class="game-score-bar">
        <span>⭐ Score: {score}</span>
        <span>🧩 {total} solved</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="logic-box">
        <div class="logic-question">{puzzle['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if not gs.get("show_result"):
        answer = st.text_input("Your answer:", key=f"lp_ans_{total}",
                               placeholder="Think carefully...")

        if st.button("✅ Submit", key=f"lp_sub_{total}", use_container_width=True):
            from modules.quiz_engine import _check_answer
            is_correct = _check_answer(answer.strip().lower(), puzzle["answer"].strip().lower())
            gs["show_result"] = True
            gs["last_correct"] = is_correct
            gs["total"] = total + 1
            if is_correct:
                gs["score"] = score + 25
            st.session_state.game_state = gs
            st.rerun()
    else:
        if gs.get("last_correct"):
            st.success(f"🎉 Brilliant! +25 points!")
        else:
            st.error(f"❌ Answer: **{puzzle['answer']}**")
        st.info(f"💡 Explanation: {puzzle.get('explanation', '')}")

        if st.button("➡️ Next Puzzle", key=f"lp_next_{total}", use_container_width=True):
            gs["current_logic"] = get_logic_puzzle()
            gs["show_result"] = False
            st.session_state.game_state = gs
            if gs["total"] >= 3:
                db.save_game_score("Brain Teaser", gs["score"], "Medium")
            st.rerun()


# ─────────────────────────────────────────────────────────
# MEMORY MATCH GAME (Card flip simulation)
# ─────────────────────────────────────────────────────────

def _game_memory_match():
    """Memory card matching game."""
    st.markdown("## 🧠 Memory Match")
    st.info("Select two cards to find matching pairs! Remember where each card is.")

    categories = list(MEMORY_SETS.keys())
    category = st.selectbox("📚 Category", categories, key="mm_category")

    gs = st.session_state.get("game_state", {})

    if "cards" not in gs or gs.get("category") != category:
        cards = get_memory_game_cards(category, pairs=6)
        gs = {
            "cards": cards,
            "category": category,
            "flipped": [],
            "matched_pairs": 0,
            "total_pairs": 6,
            "moves": 0,
            "score": 0,
            "last_flip": None
        }
        st.session_state.game_state = gs

    cards = gs["cards"]
    matched = gs["matched_pairs"]
    total_pairs = gs["total_pairs"]
    moves = gs["moves"]

    st.markdown(f"""
    <div class="game-score-bar">
        <span>🃏 Pairs: {matched}/{total_pairs}</span>
        <span>🔄 Moves: {moves}</span>
        <span>⭐ Score: {gs['score']}</span>
    </div>
    """, unsafe_allow_html=True)

    if matched >= total_pairs:
        final_score = max(0, 200 - moves * 5)
        st.success(f"🎉 You matched all pairs in {moves} moves! Score: {final_score} points!")
        db.save_game_score("Memory Match", final_score, "Medium")
        if st.button("🔄 Play Again", use_container_width=True, key="mm_restart"):
            st.session_state.game_state = {}
            st.rerun()
        return

    # Show cards in a grid
    cols_per_row = 4
    card_rows = [cards[i:i+cols_per_row] for i in range(0, len(cards), cols_per_row)]

    flipped_indices = gs["flipped"]

    for row in card_rows:
        row_cols = st.columns(len(row))
        for card, col in zip(row, row_cols):
            with col:
                card_idx = card["id"]
                is_matched = card["matched"]
                is_flipped = card_idx in flipped_indices

                if is_matched:
                    st.markdown(f"""<div class="mm-card mm-matched">
                        {card['value']}<br><small>✅</small></div>""",
                        unsafe_allow_html=True)
                elif is_flipped:
                    st.markdown(f"""<div class="mm-card mm-flipped">
                        {card['value']}</div>""", unsafe_allow_html=True)
                else:
                    if st.button("❓", key=f"mm_card_{card_idx}", use_container_width=True):
                        if len(flipped_indices) < 2 and card_idx not in flipped_indices:
                            flipped_indices.append(card_idx)
                            gs["flipped"] = flipped_indices
                            gs["moves"] = moves + 1

                            if len(flipped_indices) == 2:
                                # Check for match
                                c1 = next(c for c in cards if c["id"] == flipped_indices[0])
                                c2 = next(c for c in cards if c["id"] == flipped_indices[1])
                                if c1["pair_name"] == c2["pair_name"] and c1["id"] != c2["id"]:
                                    for c in cards:
                                        if c["id"] in flipped_indices:
                                            c["matched"] = True
                                    gs["matched_pairs"] = matched + 1
                                    gs["score"] = gs["score"] + 20
                                gs["flipped"] = []

                            st.session_state.game_state = gs
                            st.rerun()

    if flipped_indices and len(flipped_indices) < 2:
        st.info("Select another card to find the match!")
