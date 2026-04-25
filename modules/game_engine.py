"""
Game Engine - Brain development games and puzzles
"""

import random
import time

# ─────────────────────────────────────────────────────────
# MEMORY MATCH GAME
# ─────────────────────────────────────────────────────────

MEMORY_SETS = {
    "Science": [
        ("🌿", "Plants"), ("⚡", "Electricity"), ("💧", "Water"),
        ("🔥", "Fire"), ("🧪", "Chemistry"), ("🌍", "Earth"),
        ("☀️", "Sun"), ("🌙", "Moon"),
    ],
    "Animals": [
        ("🐯", "Tiger"), ("🐘", "Elephant"), ("🦁", "Lion"),
        ("🐬", "Dolphin"), ("🦅", "Eagle"), ("🐍", "Snake"),
        ("🦋", "Butterfly"), ("🐢", "Turtle"),
    ],
    "Countries": [
        ("🇮🇳", "India"), ("🇺🇸", "USA"), ("🇬🇧", "UK"),
        ("🇯🇵", "Japan"), ("🇫🇷", "France"), ("🇨🇳", "China"),
        ("🇦🇺", "Australia"), ("🇧🇷", "Brazil"),
    ],
    "Math Symbols": [
        ("➕", "Addition"), ("➖", "Subtraction"), ("✖️", "Multiplication"),
        ("➗", "Division"), ("🟰", "Equals"), ("📐", "Geometry"),
        ("📊", "Graph"), ("🔢", "Numbers"),
    ]
}


def get_memory_game_cards(category="Science", pairs=6):
    """Create shuffled memory card pairs."""
    card_set = MEMORY_SETS.get(category, MEMORY_SETS["Science"])
    selected = random.sample(card_set, min(pairs, len(card_set)))

    cards = []
    for i, (symbol, name) in enumerate(selected):
        cards.append({"id": i * 2,     "value": symbol, "pair_name": name, "flipped": False, "matched": False})
        cards.append({"id": i * 2 + 1, "value": name,   "pair_name": name, "flipped": False, "matched": False})

    random.shuffle(cards)
    return cards


# ─────────────────────────────────────────────────────────
# MATH PUZZLES
# ─────────────────────────────────────────────────────────

def get_math_puzzle(difficulty="Medium"):
    """Generate a math puzzle appropriate for Class 6."""
    if difficulty == "Easy":
        return _easy_math_puzzle()
    elif difficulty == "Hard":
        return _hard_math_puzzle()
    else:
        return _medium_math_puzzle()


def _easy_math_puzzle():
    puzzles = [
        # (question, answer, explanation)
        ("I am thinking of a number. If you add 5 to it, you get 12. What number am I thinking of?",
         "7", "12 - 5 = 7"),
        ("A bag has 20 apples. Riya takes 8. How many are left?",
         "12", "20 - 8 = 12"),
        ("5 × ? = 35. Find the missing number.",
         "7", "35 ÷ 5 = 7"),
        ("If today is Monday, what day will it be after 9 days?",
         "Wednesday", "Monday + 9 days = Wednesday (7+2 days)"),
        ("A square has side 6 cm. What is its perimeter?",
         "24 cm", "4 × 6 = 24 cm"),
        ("What comes next: 2, 4, 8, 16, ?",
         "32", "Each number doubles: 16 × 2 = 32"),
        ("How many minutes in 2 and a half hours?",
         "150 minutes", "2.5 × 60 = 150"),
    ]
    q = random.choice(puzzles)
    return {"question": q[0], "answer": q[1], "explanation": q[2], "difficulty": "Easy"}


def _medium_math_puzzle():
    puzzles = [
        ("The sum of two numbers is 50 and their difference is 10. Find the numbers.",
         "30 and 20", "Let numbers be x and y. x+y=50, x-y=10. So x=30, y=20."),
        ("A train travels 240 km in 4 hours. What is its speed?",
         "60 km/h", "Speed = Distance/Time = 240/4 = 60 km/h"),
        ("25% of a number is 75. What is the number?",
         "300", "75 is 25%, so 1% = 3, 100% = 300"),
        ("I have ₹100. I buy a book for ₹45 and a pen for ₹20. How much is left?",
         "₹35", "100 - 45 - 20 = 35"),
        ("The average of 5, 10, 15, 20, and ? is 15. Find the missing number.",
         "25", "Total = 15×5=75. Known sum=50. Missing=75-50=25"),
        ("A rectangle has length 12 cm and width 8 cm. Find its area.",
         "96 cm²", "Area = length × width = 12 × 8 = 96 cm²"),
        ("What is 3/4 of 80?",
         "60", "80 × 3/4 = 60"),
    ]
    q = random.choice(puzzles)
    return {"question": q[0], "answer": q[1], "explanation": q[2], "difficulty": "Medium"}


def _hard_math_puzzle():
    puzzles = [
        ("A shopkeeper buys an article for ₹800 and sells it for ₹1000. Find the profit percentage.",
         "25%", "Profit = 200. Profit% = (200/800)×100 = 25%"),
        ("The ratio of boys to girls in a class is 3:2. If there are 30 students, how many are girls?",
         "12 girls", "Girls = (2/5) × 30 = 12"),
        ("Solve: 4x - 7 = 2x + 9",
         "x = 8", "4x - 2x = 9 + 7 → 2x = 16 → x = 8"),
        ("A train is 200 m long and passes a pole in 20 seconds. What is its speed in km/h?",
         "36 km/h", "Speed = 200/20 = 10 m/s = 10×(18/5) = 36 km/h"),
        ("Find the LCM of 12, 18, and 24.",
         "72", "Prime factorization: 12=2²×3, 18=2×3², 24=2³×3. LCM=2³×3²=72"),
        ("The angles of a triangle are in ratio 2:3:4. Find each angle.",
         "40°, 60°, 80°", "Sum=180°. Parts=2+3+4=9. Each part=20°. Angles=40°,60°,80°"),
    ]
    q = random.choice(puzzles)
    return {"question": q[0], "answer": q[1], "explanation": q[2], "difficulty": "Hard"}


# ─────────────────────────────────────────────────────────
# WORD SCRAMBLE
# ─────────────────────────────────────────────────────────

WORD_LISTS = {
    "Science": [
        ("PHOTOSYNTHESIS", "Process by which plants make food using sunlight"),
        ("MITOCHONDRIA", "Powerhouse of the cell"),
        ("CHLOROPHYLL", "Green pigment in plants"),
        ("RESPIRATION", "Process of breathing and releasing energy"),
        ("EVAPORATION", "Water changing to vapor"),
        ("GRAVITATIONAL", "Force that pulls objects towards Earth"),
        ("REFLECTION", "Bouncing back of light"),
        ("CONDUCTORS", "Materials that allow electricity to flow"),
    ],
    "Geography": [
        ("EQUATOR", "0 degree latitude line"),
        ("LONGITUDE", "Vertical lines on globe"),
        ("PENINSULA", "Land surrounded by water on three sides"),
        ("HIMALAYAS", "Mountain range in northern India"),
        ("CONTINENT", "Large land mass on Earth"),
        ("MONSOON", "Seasonal wind bringing rain"),
        ("PLATEAU", "Flat-topped high land area"),
        ("TRIBUTARY", "River that flows into another river"),
    ],
    "History": [
        ("CIVILIZATION", "Advanced human society"),
        ("ARCHAEOLOGY", "Study of ancient remains"),
        ("DEMOCRACY", "Government by the people"),
        ("EMPEROR", "Ruler of an empire"),
        ("MANUSCRIPT", "Handwritten ancient document"),
        ("EXCAVATION", "Digging to find ancient remains"),
    ],
    "English": [
        ("ADJECTIVE", "Word that describes a noun"),
        ("VOCABULARY", "Collection of words"),
        ("PARAGRAPH", "Group of related sentences"),
        ("METAPHOR", "Comparison without using like or as"),
        ("GRAMMAR", "Rules of a language"),
        ("CONJUNCTION", "Word that joins phrases"),
    ]
}


def get_word_scramble(category="Science"):
    """Get a scrambled word puzzle."""
    word_list = WORD_LISTS.get(category, WORD_LISTS["Science"])
    word, hint = random.choice(word_list)

    # Scramble the word
    scrambled = list(word)
    while ''.join(scrambled) == word:
        random.shuffle(scrambled)
    scrambled_word = ''.join(scrambled)

    return {
        "word": word,
        "scrambled": scrambled_word,
        "hint": hint,
        "category": category,
        "length": len(word)
    }


# ─────────────────────────────────────────────────────────
# PATTERN RECOGNITION
# ─────────────────────────────────────────────────────────

def get_pattern_puzzle(difficulty="Medium"):
    """Generate a pattern recognition puzzle."""

    easy_patterns = [
        {"sequence": [2, 4, 6, 8, "?"], "answer": "10", "rule": "Add 2 each time"},
        {"sequence": [1, 3, 9, 27, "?"], "answer": "81", "rule": "Multiply by 3"},
        {"sequence": [100, 90, 80, 70, "?"], "answer": "60", "rule": "Subtract 10"},
        {"sequence": ["A", "C", "E", "G", "?"], "answer": "I", "rule": "Every other letter"},
        {"sequence": [1, 1, 2, 3, 5, "?"], "answer": "8", "rule": "Fibonacci: add previous two"},
        {"sequence": [5, 10, 20, 40, "?"], "answer": "80", "rule": "Multiply by 2"},
    ]

    medium_patterns = [
        {"sequence": [3, 6, 12, 24, "?"], "answer": "48", "rule": "Multiply by 2"},
        {"sequence": [1, 4, 9, 16, 25, "?"], "answer": "36", "rule": "Perfect squares"},
        {"sequence": [2, 6, 12, 20, 30, "?"], "answer": "42", "rule": "n×(n+1): 1×2, 2×3, 3×4..."},
        {"sequence": ["AZ", "BY", "CX", "DW", "?"], "answer": "EV", "rule": "First letter forward, second backward"},
        {"sequence": [1, 8, 27, 64, "?"], "answer": "125", "rule": "Perfect cubes (1³, 2³, 3³...)"},
    ]

    hard_patterns = [
        {"sequence": [2, 3, 5, 7, 11, 13, "?"], "answer": "17", "rule": "Prime numbers"},
        {"sequence": [0, 1, 1, 2, 3, 5, 8, "?"], "answer": "13", "rule": "Fibonacci sequence"},
        {"sequence": [1, 2, 4, 7, 11, 16, "?"], "answer": "22", "rule": "Differences increase by 1"},
        {"sequence": [3, 7, 15, 31, 63, "?"], "answer": "127", "rule": "2^n - 1 or double+1"},
    ]

    if difficulty == "Easy":
        pool = easy_patterns
    elif difficulty == "Hard":
        pool = hard_patterns
    else:
        pool = medium_patterns

    puzzle = random.choice(pool)
    return {
        "sequence": puzzle["sequence"],
        "answer": puzzle["answer"],
        "rule": puzzle["rule"],
        "difficulty": difficulty
    }


# ─────────────────────────────────────────────────────────
# VOCABULARY GAME
# ─────────────────────────────────────────────────────────

VOCAB_WORDS = [
    ("Enormous", "Very large", ["tiny", "huge", "enormous", "small"]),
    ("Transparent", "Can be seen through", ["opaque", "transparent", "cloudy", "solid"]),
    ("Fragile", "Easily broken", ["strong", "hard", "fragile", "tough"]),
    ("Ancient", "Very old", ["modern", "ancient", "new", "current"]),
    ("Curious", "Eager to learn", ["bored", "curious", "tired", "sad"]),
    ("Abundant", "Available in large quantity", ["scarce", "rare", "abundant", "few"]),
    ("Significant", "Important or meaningful", ["trivial", "significant", "minor", "tiny"]),
    ("Peculiar", "Strange or unusual", ["common", "normal", "peculiar", "regular"]),
    ("Gradually", "Slowly, step by step", ["suddenly", "gradually", "quickly", "instantly"]),
    ("Magnificent", "Impressively beautiful", ["dull", "ugly", "magnificent", "plain"]),
    ("Diligent", "Hard-working and careful", ["lazy", "careless", "diligent", "idle"]),
    ("Vibrant", "Full of energy and brightness", ["dull", "vibrant", "faded", "quiet"]),
]


def get_vocab_question():
    """Get a vocabulary question."""
    word, meaning, options = random.choice(VOCAB_WORDS)
    random.shuffle(options)
    correct_option = word

    return {
        "word": word,
        "meaning": meaning,
        "question": f"Which word means: '{meaning}'?",
        "options": options,
        "answer": word
    }


# ─────────────────────────────────────────────────────────
# LOGICAL REASONING
# ─────────────────────────────────────────────────────────

LOGIC_PUZZLES = [
    {
        "question": "🔵🔴🟢🔵🔴🟢🔵🔴__ What comes next?",
        "answer": "🟢",
        "explanation": "The pattern repeats: Blue, Red, Green"
    },
    {
        "question": "All dogs are animals. Rex is a dog. Is Rex an animal?",
        "answer": "Yes",
        "explanation": "Rex is a dog → Rex is an animal (syllogism)"
    },
    {
        "question": "If MANGO is coded as NBOHP, how is APPLE coded?",
        "answer": "BQQMF",
        "explanation": "Each letter is replaced by the next letter in the alphabet"
    },
    {
        "question": "A is taller than B. B is taller than C. Who is the shortest?",
        "answer": "C",
        "explanation": "A > B > C, so C is shortest"
    },
    {
        "question": "What has hands but cannot clap? 🤔",
        "answer": "A clock",
        "explanation": "A clock has hands (hour and minute hand) but cannot clap!"
    },
    {
        "question": "I speak without a mouth and hear without ears. What am I?",
        "answer": "An echo",
        "explanation": "An echo reflects sound back without a mouth or ears"
    },
    {
        "question": "If 2 + 2 = 4, 3 + 3 = 9, 4 + 4 = 16, what is 5 + 5?",
        "answer": "25",
        "explanation": "The pattern is n + n = n² (square of n). So 5² = 25"
    },
    {
        "question": "Monday's child is 10 years old. In 4 years, she will be twice as old as her brother. How old is the brother now?",
        "answer": "3 years old",
        "explanation": "In 4 years: sister=14, brother=7. Currently: 7-4=3"
    }
]


def get_logic_puzzle():
    """Get a random logic puzzle."""
    return random.choice(LOGIC_PUZZLES)


# ─────────────────────────────────────────────────────────
# GAME CATALOG
# ─────────────────────────────────────────────────────────

GAMES_CATALOG = [
    {"id": "memory_match",  "name": "Memory Match",     "icon": "🧠", "desc": "Match pairs of cards!",              "category": "Memory"},
    {"id": "math_puzzle",   "name": "Math Puzzle",       "icon": "🔢", "desc": "Solve tricky math problems!",        "category": "Math"},
    {"id": "word_scramble", "name": "Word Scramble",     "icon": "📝", "desc": "Unscramble the mixed-up words!",     "category": "Language"},
    {"id": "pattern_game",  "name": "Pattern Detective", "icon": "🔍", "desc": "Find what comes next in patterns!",  "category": "Logic"},
    {"id": "vocab_game",    "name": "Vocabulary Quiz",   "icon": "📚", "desc": "Build your vocabulary!",             "category": "Language"},
    {"id": "logic_puzzle",  "name": "Brain Teaser",      "icon": "💡", "desc": "Test your logical thinking!",        "category": "Logic"},
    {"id": "rapid_fire",    "name": "Rapid Fire Quiz",   "icon": "⚡", "desc": "Answer 10 questions in 60 seconds!", "category": "Speed"},
]
