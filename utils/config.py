"""
Configuration file for AI Home Tutor
All constants, subjects, syllabus content, and settings
"""

import os

# ─────────────────────────────────────────────────────────
# APP SETTINGS
# ─────────────────────────────────────────────────────────
APP_TITLE = "🎓 AI Home Tutor - Class 6 ICSE"
APP_VERSION = "1.0.0"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(DATA_DIR, "tutor.db")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# ─────────────────────────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────────────────────────
SUBJECTS = [
    {"id": "english",    "name": "English",          "icon": "📖", "color": "#FF6B6B", "bg": "#FFE5E5"},
    {"id": "bengali",    "name": "Bengali",           "icon": "বাং", "color": "#4ECDC4", "bg": "#E5F9F8"},
    {"id": "hindi",      "name": "Hindi",             "icon": "हि",  "color": "#45B7D1", "bg": "#E5F4FB"},
    {"id": "mathematics","name": "Mathematics",       "icon": "🔢", "color": "#6C5CE7", "bg": "#EDE9FF"},
    {"id": "biology",    "name": "Biology",           "icon": "🌿", "color": "#00B894", "bg": "#E5F8F3"},
    {"id": "physics",    "name": "Physics",           "icon": "⚡", "color": "#FDCB6E", "bg": "#FFF8E5"},
    {"id": "chemistry",  "name": "Chemistry",         "icon": "🧪", "color": "#E17055", "bg": "#FFF0EC"},
    {"id": "history",    "name": "History",           "icon": "🏛️", "color": "#A29BFE", "bg": "#F0EEFF"},
    {"id": "geography",  "name": "Geography",         "icon": "🌍", "color": "#55EFC4", "bg": "#E5FFF8"},
    {"id": "computer",   "name": "Computer Studies",  "icon": "💻", "color": "#74B9FF", "bg": "#E8F4FF"},
    {"id": "gk",         "name": "General Knowledge", "icon": "🌟", "color": "#FD79A8", "bg": "#FFE8F2"},
    {"id": "moral",      "name": "Moral Science",     "icon": "🌸", "color": "#B8E994", "bg": "#F0FAE8"},
    {"id": "ai_robotics","name": "AI & Robotics",     "icon": "🤖", "color": "#81ECEC", "bg": "#E5FAFA"},
]

SUBJECT_IDS = [s["id"] for s in SUBJECTS]


# ─────────────────────────────────────────────────────────
# DYNAMIC CURRICULUM ACCESSORS (Phase 4)
# ─────────────────────────────────────────────────────────
# Consumers should now call get_subjects() / get_syllabus() / get_subject()
# to pick up live edits made via the Admin Curriculum UI. The constants
# above (SUBJECTS, SYLLABUS) remain as the SEED data used on first run.

def get_subjects():
    """Live list of subjects from the curriculum DB. Falls back to SUBJECTS."""
    try:
        from utils.curriculum import get_all_subjects
        return get_all_subjects()
    except Exception:
        return SUBJECTS


def get_syllabus():
    """Live syllabus dict from the curriculum DB. Falls back to SYLLABUS."""
    try:
        from utils.curriculum import get_syllabus as _live
        return _live()
    except Exception:
        return SYLLABUS


def get_subject(subject_id):
    """Live single-subject lookup; falls back to seed list if DB unavailable."""
    try:
        from utils.curriculum import get_subject as _live
        return _live(subject_id)
    except Exception:
        for s in SUBJECTS:
            if s["id"] == subject_id:
                return s
        return SUBJECTS[0]

# ─────────────────────────────────────────────────────────
# ICSE CLASS 6 SYLLABUS (Built-in content)
# ─────────────────────────────────────────────────────────
SYLLABUS = {
    "english": {
        "chapters": [
            {
                "id": 1, "title": "Parts of Speech",
                "topics": ["Nouns", "Pronouns", "Adjectives", "Verbs", "Adverbs", "Prepositions", "Conjunctions", "Interjections"],
                "explanation": "Parts of speech are the categories that words are placed in based on how they are used in a sentence. There are 8 parts of speech in English grammar.",
                "key_points": [
                    "A Noun is a naming word: cat, school, happiness",
                    "A Pronoun replaces a noun: he, she, they, it",
                    "An Adjective describes a noun: big, beautiful, three",
                    "A Verb shows action or state: run, is, think",
                    "An Adverb modifies verb/adjective: quickly, very, always",
                    "A Preposition shows relation: in, on, under, between",
                    "A Conjunction joins words/clauses: and, but, because",
                    "An Interjection shows emotion: Oh!, Wow!, Hurray!"
                ],
                "examples": [
                    "The big dog (adjective) runs (verb) quickly (adverb) in (preposition) the park.",
                    "Ram and (conjunction) Sita went to the market.",
                    "Wow! (interjection) That is amazing!"
                ],
                "questions": [
                    {"q": "What is a noun?", "a": "A noun is a naming word that refers to a person, place, thing, or idea.", "type": "short"},
                    {"q": "Identify the verb: 'The bird sings sweetly.'", "a": "sings", "type": "identify"},
                    {"q": "How many parts of speech are there in English?", "a": "8", "type": "mcq", "options": ["6", "7", "8", "9"]},
                    {"q": "Which part of speech is 'beautiful'?", "a": "Adjective", "type": "mcq", "options": ["Noun", "Verb", "Adjective", "Adverb"]},
                    {"q": "Give 3 examples of pronouns.", "a": "he, she, they, it, we, I, you (any 3)", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Tenses",
                "topics": ["Simple Present", "Present Continuous", "Simple Past", "Past Continuous", "Simple Future"],
                "explanation": "Tenses tell us WHEN an action happens - in the past, present, or future. Understanding tenses helps us speak and write correctly.",
                "key_points": [
                    "Simple Present: I eat (habit/fact) - adds -s/-es for he/she/it",
                    "Present Continuous: I am eating (happening now) - use am/is/are + verb-ing",
                    "Simple Past: I ate (completed action) - add -ed or irregular forms",
                    "Past Continuous: I was eating (was happening) - use was/were + verb-ing",
                    "Simple Future: I will eat (future action) - use will/shall + verb"
                ],
                "examples": [
                    "She plays tennis every day. (Simple Present)",
                    "He is reading a book right now. (Present Continuous)",
                    "They played cricket yesterday. (Simple Past)",
                    "I will help you tomorrow. (Simple Future)"
                ],
                "questions": [
                    {"q": "Change to Simple Past: 'She writes a letter.'", "a": "She wrote a letter.", "type": "transform"},
                    {"q": "Which tense is: 'They are dancing.'?", "a": "Present Continuous", "type": "identify"},
                    {"q": "Fill in the blank: 'He ___ (go) to school yesterday.'", "a": "went", "type": "fill"},
                ]
            },
            {
                "id": 3, "title": "Comprehension & Reading",
                "topics": ["Reading passages", "Finding main idea", "Inference", "Vocabulary in context"],
                "explanation": "Comprehension means understanding what you read. Good readers find the main idea, understand new words from context, and make inferences.",
                "key_points": [
                    "Always read the passage twice before answering",
                    "Look for the main idea in the first or last sentence of each paragraph",
                    "For vocabulary questions, look at surrounding words for clues",
                    "Inference means finding what is not directly stated"
                ],
                "examples": [],
                "questions": []
            },
            {
                "id": 4, "title": "Writing Skills",
                "topics": ["Essay writing", "Letter writing", "Story writing", "Notice writing"],
                "explanation": "Good writing has a clear structure: Introduction, Body, and Conclusion. Always plan before you write!",
                "key_points": [
                    "Formal letter: Sender's address → Date → Receiver's address → Salutation → Body → Closing",
                    "Essay: Introduction (what you'll discuss) → Body (3-4 paragraphs) → Conclusion",
                    "Story: Must have characters, setting, plot, problem, and solution"
                ],
                "examples": [],
                "questions": []
            }
        ]
    },
    "mathematics": {
        "chapters": [
            {
                "id": 1, "title": "Number System",
                "topics": ["Natural Numbers", "Whole Numbers", "Integers", "Number Line", "Place Value"],
                "explanation": "Numbers are everywhere! The number system helps us count, measure, and calculate. In Class 6, we learn about different types of numbers and how they work.",
                "key_points": [
                    "Natural Numbers: 1, 2, 3, 4, 5... (counting numbers)",
                    "Whole Numbers: 0, 1, 2, 3, 4... (natural numbers + zero)",
                    "Integers: ...-3, -2, -1, 0, 1, 2, 3... (positive and negative)",
                    "Place Value: In 4,567 → 4=thousands, 5=hundreds, 6=tens, 7=ones",
                    "Number Line: Numbers increase to the right, decrease to the left"
                ],
                "examples": [
                    "3 + (-5) = -2 (on number line, go 3 right then 5 left)",
                    "Place value of 6 in 7,652 = 6 × 100 = 600",
                    "(-3) × (-2) = +6 (negative × negative = positive)"
                ],
                "questions": [
                    {"q": "What is the place value of 5 in 35,867?", "a": "5000 (thousands place)", "type": "short"},
                    {"q": "Which is greater: -3 or -7?", "a": "-3 (closer to 0 on number line)", "type": "short"},
                    {"q": "Calculate: -8 + 5", "a": "-3", "type": "calculate"},
                    {"q": "What are whole numbers?", "a": "Natural numbers including zero: 0, 1, 2, 3...", "type": "short"},
                    {"q": "Write the predecessor of -5.", "a": "-6", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Fractions & Decimals",
                "topics": ["Types of fractions", "Operations on fractions", "Decimal notation", "Conversion"],
                "explanation": "Fractions represent parts of a whole. If you cut a pizza into 4 equal slices and take 3, you have 3/4 of the pizza!",
                "key_points": [
                    "Proper fraction: numerator < denominator (3/4)",
                    "Improper fraction: numerator > denominator (5/3)",
                    "Mixed number: whole + fraction (1 2/3)",
                    "Like fractions have same denominator",
                    "To add/subtract fractions: make denominators equal first",
                    "To multiply fractions: multiply numerators, multiply denominators",
                    "To divide fractions: multiply by the reciprocal"
                ],
                "examples": [
                    "1/3 + 1/6 = 2/6 + 1/6 = 3/6 = 1/2",
                    "3/4 × 2/5 = 6/20 = 3/10",
                    "0.75 = 75/100 = 3/4"
                ],
                "questions": [
                    {"q": "Add: 2/5 + 3/10", "a": "4/10 + 3/10 = 7/10", "type": "calculate"},
                    {"q": "What is the reciprocal of 3/7?", "a": "7/3", "type": "short"},
                    {"q": "Convert 0.6 to a fraction.", "a": "6/10 = 3/5", "type": "calculate"},
                    {"q": "Multiply: 1/4 × 8", "a": "2", "type": "calculate"},
                ]
            },
            {
                "id": 3, "title": "Algebra - Introduction",
                "topics": ["Variables", "Constants", "Expressions", "Simple equations"],
                "explanation": "Algebra uses letters (like x, y) to represent unknown numbers. It's like solving a mystery - finding the value of the unknown!",
                "key_points": [
                    "Variable: a letter representing unknown value (x, y, n)",
                    "Constant: a fixed number (3, -7, 100)",
                    "Expression: combination of variables and constants (2x + 5)",
                    "Equation: expression with = sign (2x + 5 = 11)",
                    "To solve equation: do same operation on both sides"
                ],
                "examples": [
                    "Solve: x + 7 = 12 → x = 12 - 7 = 5",
                    "Solve: 3n = 18 → n = 18 ÷ 3 = 6",
                    "If a = 3, find 2a + 1 = 2(3) + 1 = 7"
                ],
                "questions": [
                    {"q": "Solve: x + 5 = 12", "a": "x = 7", "type": "calculate"},
                    {"q": "If p = 4, find 3p - 2.", "a": "10", "type": "calculate"},
                    {"q": "Solve: 4y = 20", "a": "y = 5", "type": "calculate"},
                ]
            },
            {
                "id": 4, "title": "Geometry",
                "topics": ["Points, Lines, Angles", "Types of triangles", "Quadrilaterals", "Circles"],
                "explanation": "Geometry is the study of shapes, sizes, and positions of figures. Everything around us has a geometric shape!",
                "key_points": [
                    "Point: exact location (no size)",
                    "Line: extends infinitely in both directions",
                    "Angle types: Acute (<90°), Right (=90°), Obtuse (>90°, <180°)",
                    "Triangle types by angle: Acute, Right, Obtuse",
                    "Triangle types by side: Equilateral (3 equal), Isosceles (2 equal), Scalene (all different)",
                    "Sum of angles in triangle = 180°",
                    "Quadrilateral: 4-sided polygon, sum of angles = 360°"
                ],
                "examples": [
                    "In a triangle with angles 60° and 70°, third angle = 180-60-70 = 50°",
                    "A rectangle has 4 right angles and opposite sides equal"
                ],
                "questions": [
                    {"q": "What is the sum of angles in a triangle?", "a": "180 degrees", "type": "short"},
                    {"q": "A triangle has angles 50° and 70°. Find the third angle.", "a": "60°", "type": "calculate"},
                    {"q": "What type of angle is 135°?", "a": "Obtuse angle", "type": "mcq", "options": ["Acute", "Right", "Obtuse", "Reflex"]},
                ]
            },
            {
                "id": 5, "title": "Ratio & Proportion",
                "topics": ["Ratio", "Proportion", "Unitary method", "Percentage"],
                "explanation": "Ratio compares two quantities. Proportion means two ratios are equal. These are used in cooking, maps, mixing, and everyday life!",
                "key_points": [
                    "Ratio a:b = a/b (both in same unit)",
                    "Proportion: a:b = c:d means a×d = b×c (cross multiplication)",
                    "Unitary method: find value of 1 unit, then multiply",
                    "Percentage: per hundred (%), convert to fraction by ÷100"
                ],
                "examples": [
                    "Ratio of 30 to 50 = 30:50 = 3:5",
                    "If 5 pens cost ₹30, 8 pens cost = (30/5)×8 = ₹48",
                    "25% of 80 = (25/100) × 80 = 20"
                ],
                "questions": [
                    {"q": "Simplify ratio 24:36", "a": "2:3", "type": "calculate"},
                    {"q": "If 4 kg costs ₹60, find cost of 7 kg.", "a": "₹105", "type": "calculate"},
                    {"q": "Find 30% of 150.", "a": "45", "type": "calculate"},
                ]
            }
        ]
    },
    "biology": {
        "chapters": [
            {
                "id": 1, "title": "The Living World",
                "topics": ["Characteristics of living things", "Classification", "Taxonomy basics"],
                "explanation": "The living world is full of amazing organisms! From tiny bacteria to giant whales, all living things share certain characteristics that make them different from non-living things.",
                "key_points": [
                    "Characteristics of living things: Movement, Respiration, Growth, Reproduction, Nutrition, Excretion, Response to stimuli",
                    "Mnemonic: MRGREN (Movement, Respiration, Growth, Reproduction, Excretion, Nutrition)",
                    "Classification: Kingdom → Phylum → Class → Order → Family → Genus → Species",
                    "Five Kingdoms: Monera, Protista, Fungi, Plantae, Animalia"
                ],
                "examples": [
                    "Plants respond to light (phototropism) - they grow towards sunlight",
                    "Fire is not living - it moves and grows but cannot reproduce or excrete"
                ],
                "questions": [
                    {"q": "List 5 characteristics of living organisms.", "a": "Movement, Respiration, Growth, Reproduction, Nutrition, Excretion (any 5)", "type": "short"},
                    {"q": "What is the full form of the classification system?", "a": "Kingdom, Phylum, Class, Order, Family, Genus, Species", "type": "short"},
                    {"q": "Is fire a living thing? Why?", "a": "No - fire cannot reproduce, excrete, or show all life processes", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "The Cell",
                "topics": ["Cell theory", "Plant vs Animal cell", "Cell organelles", "Cell division"],
                "explanation": "The cell is the basic unit of life! Just like a building is made of bricks, your body is made of trillions of tiny cells. Each cell has a job to do.",
                "key_points": [
                    "Cell Theory: All living things are made of cells; cell is the basic unit of life; all cells come from existing cells",
                    "Cell membrane: controls what enters/exits the cell",
                    "Nucleus: the 'brain' of the cell, contains DNA",
                    "Mitochondria: the 'powerhouse', produces energy (ATP)",
                    "Chloroplast: found only in plant cells, for photosynthesis",
                    "Cell wall: found only in plant cells (rigid outer layer)",
                    "Vacuole: storage; large in plant cells, small in animal cells"
                ],
                "examples": [
                    "Red blood cells have no nucleus (to carry more hemoglobin)",
                    "Muscle cells have many mitochondria (need lots of energy)"
                ],
                "questions": [
                    {"q": "What is the powerhouse of the cell?", "a": "Mitochondria", "type": "short"},
                    {"q": "Name 2 structures found in plant cells but NOT in animal cells.", "a": "Cell wall and Chloroplast", "type": "short"},
                    {"q": "What does the nucleus contain?", "a": "DNA (genetic material)", "type": "short"},
                    {"q": "What is the cell membrane?", "a": "A thin, flexible layer that controls what enters and exits the cell", "type": "short"},
                ]
            },
            {
                "id": 3, "title": "Plant Life",
                "topics": ["Photosynthesis", "Transpiration", "Parts of a plant", "Reproduction in plants"],
                "explanation": "Plants are amazing living factories! They make their own food using sunlight, water, and carbon dioxide. This process is called photosynthesis.",
                "key_points": [
                    "Photosynthesis equation: CO2 + H2O + Sunlight → Glucose + O2",
                    "Photosynthesis happens in chloroplasts (which contain chlorophyll)",
                    "Chlorophyll is the green pigment that absorbs sunlight",
                    "Transpiration: loss of water through stomata (tiny pores in leaves)",
                    "Root functions: absorb water & minerals, anchor plant",
                    "Stem functions: transport water & food, support plant"
                ],
                "examples": [
                    "A green leaf placed in sunlight releases oxygen bubbles (photosynthesis)",
                    "Leaves wilt on hot days due to excess transpiration"
                ],
                "questions": [
                    {"q": "Write the equation for photosynthesis.", "a": "CO2 + H2O + Sunlight energy → Glucose + O2", "type": "short"},
                    {"q": "What is chlorophyll?", "a": "The green pigment in plants that absorbs sunlight for photosynthesis", "type": "short"},
                    {"q": "What is transpiration?", "a": "The loss of water vapour through stomata in leaves", "type": "short"},
                ]
            }
        ]
    },
    "physics": {
        "chapters": [
            {
                "id": 1, "title": "Measurement",
                "topics": ["SI units", "Length measurement", "Mass and weight", "Time measurement", "Instruments"],
                "explanation": "Measurement is comparing a quantity with a standard unit. Scientists use the SI system (International System of Units) worldwide so everyone understands each other!",
                "key_points": [
                    "SI unit of length: metre (m)",
                    "SI unit of mass: kilogram (kg)",
                    "SI unit of time: second (s)",
                    "1 km = 1000 m; 1 m = 100 cm; 1 cm = 10 mm",
                    "1 tonne = 1000 kg; 1 kg = 1000 g; 1 g = 1000 mg",
                    "Instruments: ruler/metre scale (length), balance (mass), clock (time), thermometer (temperature)"
                ],
                "examples": [
                    "A cricket pitch is 20.12 metres long",
                    "Your textbook has a mass of about 500 grams (0.5 kg)"
                ],
                "questions": [
                    {"q": "What is the SI unit of mass?", "a": "Kilogram (kg)", "type": "short"},
                    {"q": "Convert 3.5 km to metres.", "a": "3500 m", "type": "calculate"},
                    {"q": "Name the instrument used to measure temperature.", "a": "Thermometer", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Forces and Motion",
                "topics": ["Types of forces", "Effects of force", "Newton's laws basics", "Friction"],
                "explanation": "A force is a push or pull that can change the motion, shape, or direction of an object. Forces are everywhere - gravity pulls you down, friction stops you from slipping!",
                "key_points": [
                    "Force can: change speed, change direction, change shape",
                    "Types: Gravitational, Magnetic, Electrostatic, Muscular, Frictional, Normal",
                    "Friction: force that opposes motion between surfaces",
                    "Friction is useful (brakes, writing) and sometimes a problem (machinery wear)",
                    "Gravity: force that pulls objects towards Earth's centre"
                ],
                "examples": [
                    "Kicking a football (force changes its motion)",
                    "Brakes on a bicycle use friction to stop it"
                ],
                "questions": [
                    {"q": "What is a force?", "a": "A push or pull that can change the motion, shape, or direction of an object", "type": "short"},
                    {"q": "Name 3 effects of force.", "a": "Change speed, change direction, change shape", "type": "short"},
                    {"q": "What is friction?", "a": "A force that opposes the relative motion between two surfaces in contact", "type": "short"},
                ]
            },
            {
                "id": 3, "title": "Light",
                "topics": ["Sources of light", "Reflection", "Laws of reflection", "Mirrors"],
                "explanation": "Light is a form of energy that helps us see! It travels in straight lines at an incredible speed of 3,00,000 km per second. That's fast enough to go around Earth 7.5 times in one second!",
                "key_points": [
                    "Speed of light: 3 × 10^8 m/s (300,000 km/s)",
                    "Light travels in straight lines (rectilinear propagation)",
                    "Laws of Reflection: Angle of incidence = Angle of reflection",
                    "Plane mirror: virtual, erect, laterally inverted, same size image",
                    "Concave mirror: converging, used in torches, telescopes",
                    "Convex mirror: diverging, used as rear-view mirrors (wider field)"
                ],
                "examples": [
                    "Shadow formation proves light travels in straight lines",
                    "Echo is to sound what reflection is to light"
                ],
                "questions": [
                    {"q": "State the laws of reflection.", "a": "1) Angle of incidence = Angle of reflection. 2) Incident ray, reflected ray, and normal are in the same plane.", "type": "short"},
                    {"q": "Why is a convex mirror used as a rear-view mirror?", "a": "It gives a wider field of view as it diverges light", "type": "short"},
                    {"q": "What is the speed of light?", "a": "3 × 10^8 m/s or 3,00,000 km/s", "type": "short"},
                ]
            }
        ]
    },
    "chemistry": {
        "chapters": [
            {
                "id": 1, "title": "Matter and Its Properties",
                "topics": ["States of matter", "Properties of matter", "Changes in matter"],
                "explanation": "Matter is anything that has mass and occupies space. Everything around you - air, water, your book, you - is matter! Matter can exist in three main states.",
                "key_points": [
                    "Three states of matter: Solid, Liquid, Gas",
                    "Solid: definite shape and volume, particles tightly packed",
                    "Liquid: definite volume but no fixed shape, particles loosely packed",
                    "Gas: no fixed shape or volume, particles far apart and move freely",
                    "Physical change: no new substance formed (melting, dissolving)",
                    "Chemical change: new substance formed (burning, rusting, cooking)"
                ],
                "examples": [
                    "Ice → Water → Steam (all H2O, different states)",
                    "Burning paper = chemical change (new substances: ash, CO2)",
                    "Folding paper = physical change (same substance)"
                ],
                "questions": [
                    {"q": "What are the three states of matter?", "a": "Solid, Liquid, Gas", "type": "short"},
                    {"q": "Is dissolving sugar in water a physical or chemical change?", "a": "Physical change (sugar can be recovered by evaporating water)", "type": "short"},
                    {"q": "Name 2 differences between solids and liquids.", "a": "Solid has definite shape; liquid does not. Solid particles are more tightly packed.", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Elements, Compounds & Mixtures",
                "topics": ["Elements", "Compounds", "Mixtures", "Separation methods"],
                "explanation": "Everything is made of elements (like LEGO blocks)! When elements combine chemically, they form compounds. Mixtures are physical combinations that can be separated.",
                "key_points": [
                    "Element: purest form, cannot be broken down further (Gold, Oxygen, Carbon)",
                    "Compound: two or more elements chemically combined (Water H2O, Salt NaCl)",
                    "Mixture: substances physically mixed (Salad, Air, Sea water)",
                    "Separation methods: Filtration, Evaporation, Distillation, Magnetic separation, Sedimentation"
                ],
                "examples": [
                    "Water (H2O) = Hydrogen + Oxygen chemically bonded",
                    "Air is a mixture of N2, O2, CO2, and other gases",
                    "Separating iron filings from sand: use a magnet"
                ],
                "questions": [
                    {"q": "What is the chemical formula of water?", "a": "H2O", "type": "short"},
                    {"q": "How would you separate a mixture of salt and water?", "a": "Evaporation (heat the mixture, water evaporates, salt remains)", "type": "short"},
                    {"q": "Is air a mixture or compound? Why?", "a": "Mixture - it contains various gases in variable proportions that can be separated", "type": "short"},
                ]
            }
        ]
    },
    "history": {
        "chapters": [
            {
                "id": 1, "title": "Early Civilizations",
                "topics": ["Indus Valley Civilization", "Mesopotamia", "Egyptian Civilization", "Chinese Civilization"],
                "explanation": "Thousands of years ago, humans stopped wandering and settled down near rivers. These settlements grew into great civilizations! The oldest ones were in Asia and Africa.",
                "key_points": [
                    "Indus Valley Civilization (3300-1300 BCE): Harappa and Mohenjo-daro",
                    "Well-planned cities with drainage systems, granaries, and baths",
                    "Mesopotamia (Iraq): between rivers Tigris and Euphrates, invented writing (cuneiform)",
                    "Egypt: along River Nile, famous for pyramids and mummies",
                    "China: along Yellow River (Huang He), invented paper and silk"
                ],
                "examples": [
                    "The Great Bath of Mohenjo-daro shows advanced water management",
                    "Pyramids of Giza were built as royal tombs (around 2500 BCE)"
                ],
                "questions": [
                    {"q": "Name the two major cities of the Indus Valley Civilization.", "a": "Harappa and Mohenjo-daro", "type": "short"},
                    {"q": "Which river was important for the Egyptian Civilization?", "a": "River Nile", "type": "short"},
                    {"q": "What did Mesopotamians invent?", "a": "Writing (Cuneiform script)", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Ancient India",
                "topics": ["Vedic Age", "Mahajanapadas", "Mauryan Empire", "Gupta Empire"],
                "explanation": "Ancient India was one of the world's greatest civilizations. It gave the world zero, chess, yoga, and many scientific discoveries. Let's explore India's glorious past!",
                "key_points": [
                    "Vedic Age (1500-600 BCE): Aryans composed the Vedas (Rigveda is oldest)",
                    "16 Mahajanapadas (600-400 BCE): major kingdoms/republics",
                    "Mauryan Empire (321-185 BCE): founded by Chandragupta Maurya",
                    "Ashoka the Great: spread Buddhism after Kalinga War",
                    "Gupta Empire (320-550 CE): 'Golden Age of India' - art, science, literature"
                ],
                "examples": [
                    "Aryabhata (Gupta period) discovered zero and calculated value of π",
                    "Ashoka's pillars with Dhamma edicts are found across India"
                ],
                "questions": [
                    {"q": "Who founded the Mauryan Empire?", "a": "Chandragupta Maurya", "type": "short"},
                    {"q": "Why is the Gupta period called the Golden Age of India?", "a": "Great achievements in art, science, literature and mathematics", "type": "short"},
                    {"q": "What is the Rigveda?", "a": "The oldest Veda, a collection of hymns composed during the Vedic Age", "type": "short"},
                ]
            }
        ]
    },
    "geography": {
        "chapters": [
            {
                "id": 1, "title": "The Earth and Globe",
                "topics": ["Shape of Earth", "Latitudes and Longitudes", "Time zones", "Movements of Earth"],
                "explanation": "Earth is our beautiful home in space! It's shaped like a ball (sphere) - slightly flattened at the poles. We use a globe to represent Earth and a map to show it on a flat surface.",
                "key_points": [
                    "Earth's shape: Oblate spheroid (flattened at poles, bulging at equator)",
                    "Latitude: horizontal lines, measure N-S distance from Equator (0°-90°)",
                    "Longitude: vertical lines, measure E-W distance from Prime Meridian (0°-180°)",
                    "Equator: 0° latitude, divides Earth into Northern and Southern Hemisphere",
                    "Prime Meridian: 0° longitude, passes through Greenwich, England",
                    "Rotation: Earth spins on axis (West to East) in 24 hours → day and night",
                    "Revolution: Earth orbits Sun in 365.25 days → seasons"
                ],
                "examples": [
                    "India is located between latitudes 8°N and 37°N",
                    "When it's 12 noon in London, it's 5:30 PM in India (IST = GMT + 5:30)"
                ],
                "questions": [
                    {"q": "What is the shape of the Earth?", "a": "Oblate spheroid (slightly flattened at poles)", "type": "short"},
                    {"q": "What causes day and night?", "a": "Earth's rotation on its own axis (every 24 hours)", "type": "short"},
                    {"q": "What is the Prime Meridian?", "a": "0° longitude line passing through Greenwich, England", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "India - Physical Features",
                "topics": ["Himalayan mountains", "Indo-Gangetic Plain", "Peninsular Plateau", "Coastal Plains", "Islands"],
                "explanation": "India is a land of amazing diversity! From the mighty Himalayas in the north to the tropical beaches in the south, India has every type of landscape.",
                "key_points": [
                    "India's land area: 3.28 million km² (7th largest country)",
                    "Northern Mountains: Himalayas (young fold mountains), highest peak in India = Kangchenjunga",
                    "Northern Plains: formed by rivers Indus, Ganga, Brahmaputra - very fertile",
                    "Peninsular Plateau: oldest landmass, made of ancient rocks, rich in minerals",
                    "Coastal Plains: Eastern (broader, deltas) and Western (narrow, steep)",
                    "Islands: Andaman & Nicobar (Bay of Bengal), Lakshadweep (Arabian Sea)"
                ],
                "examples": [
                    "Mount Everest (8848m) is in Nepal-Tibet border (not in India)",
                    "The Deccan Plateau is rich in cotton soil (black soil) - great for cotton farming"
                ],
                "questions": [
                    {"q": "What is the highest peak of India?", "a": "Kangchenjunga (8586 m)", "type": "short"},
                    {"q": "Name the rivers that form the Northern Plains of India.", "a": "Indus, Ganga, and Brahmaputra", "type": "short"},
                    {"q": "Where are the Andaman and Nicobar Islands located?", "a": "Bay of Bengal", "type": "short"},
                ]
            }
        ]
    },
    "computer": {
        "chapters": [
            {
                "id": 1, "title": "Introduction to Computers",
                "topics": ["History of computers", "Types of computers", "Computer hardware", "Computer software"],
                "explanation": "A computer is an electronic device that can process, store, and display information. It follows your instructions very quickly and accurately!",
                "key_points": [
                    "Computer: Input → Process → Output → Storage",
                    "Hardware: Physical parts (CPU, Monitor, Keyboard, Mouse, RAM)",
                    "Software: Programs (Windows, MS Word, Games)",
                    "CPU (Central Processing Unit): 'brain' of the computer",
                    "RAM: temporary memory while computer is on",
                    "ROM: permanent memory, contains startup instructions",
                    "Types: Supercomputer, Mainframe, Mini, Micro (Desktop/Laptop/Tablet)"
                ],
                "examples": [
                    "Keyboard and mouse are Input devices",
                    "Monitor and printer are Output devices",
                    "Hard disk is a Storage device"
                ],
                "questions": [
                    {"q": "What is the full form of CPU?", "a": "Central Processing Unit", "type": "short"},
                    {"q": "Classify: Monitor, Keyboard, Printer, Mouse", "a": "Input: Keyboard, Mouse | Output: Monitor, Printer", "type": "classify"},
                    {"q": "What is the difference between RAM and ROM?", "a": "RAM is temporary memory (lost when power off); ROM is permanent memory", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Operating System & MS Office",
                "topics": ["Windows OS", "File management", "MS Word basics", "MS Excel basics", "Internet basics"],
                "explanation": "An Operating System (OS) is the main software that manages all other programs and hardware. Windows is the most popular OS for home computers.",
                "key_points": [
                    "OS functions: Manages hardware, runs programs, provides user interface",
                    "Windows: Most popular desktop OS by Microsoft",
                    "Desktop, Taskbar, Start Menu, Windows Explorer are parts of Windows",
                    "MS Word: word processing (documents, letters)",
                    "MS Excel: spreadsheets (tables, calculations, graphs)",
                    "MS PowerPoint: presentations (slides)"
                ],
                "examples": [
                    "Ctrl+C = Copy, Ctrl+V = Paste, Ctrl+Z = Undo",
                    "File extensions: .doc/.docx (Word), .xls/.xlsx (Excel), .ppt/.pptx (PowerPoint)"
                ],
                "questions": [
                    {"q": "What is an operating system?", "a": "Software that manages hardware and provides a platform for running other programs", "type": "short"},
                    {"q": "What keyboard shortcut is used to Save a file?", "a": "Ctrl + S", "type": "short"},
                    {"q": "Name 3 Microsoft Office applications.", "a": "MS Word, MS Excel, MS PowerPoint", "type": "short"},
                ]
            }
        ]
    },
    "gk": {
        "chapters": [
            {
                "id": 1, "title": "India - General Knowledge",
                "topics": ["National symbols", "States and capitals", "Important leaders", "Famous landmarks"],
                "explanation": "India is incredible! The world's largest democracy with 1.4 billion people, 22 official languages, and thousands of years of history. Let's learn some amazing facts!",
                "key_points": [
                    "National Animal: Bengal Tiger 🐯", "National Bird: Indian Peacock 🦚",
                    "National Flower: Lotus 🌸", "National Tree: Banyan", "National Fruit: Mango 🥭",
                    "National Game: Field Hockey", "National Song: Vande Mataram",
                    "National Anthem: Jana Gana Mana (written by Rabindranath Tagore)",
                    "Capital: New Delhi", "Currency: Indian Rupee (₹)",
                    "Population: ~140 crore (1.4 billion)", "Area: 3.28 million sq km"
                ],
                "examples": [],
                "questions": [
                    {"q": "What is the national animal of India?", "a": "Bengal Tiger", "type": "short"},
                    {"q": "Who wrote the National Anthem 'Jana Gana Mana'?", "a": "Rabindranath Tagore", "type": "short"},
                    {"q": "What is the national flower of India?", "a": "Lotus", "type": "short"},
                    {"q": "How many states are there in India?", "a": "28 states and 8 Union Territories", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "World General Knowledge",
                "topics": ["World records", "Countries and capitals", "Famous inventions", "Space and science"],
                "explanation": "The world is full of amazing facts! From the tallest mountain to the deepest ocean, let's explore some incredible knowledge about our world.",
                "key_points": [
                    "Largest continent: Asia", "Smallest continent: Australia",
                    "Largest ocean: Pacific Ocean", "Deepest ocean: Pacific (Mariana Trench ~11km)",
                    "Tallest mountain: Mount Everest (8,848.86 m)",
                    "Longest river: Amazon (by volume) / Nile (by length)",
                    "Largest country by area: Russia", "Most populous country: India",
                    "Inventor of telephone: Alexander Graham Bell",
                    "First person on Moon: Neil Armstrong (July 1969)"
                ],
                "examples": [],
                "questions": [
                    {"q": "What is the tallest mountain in the world?", "a": "Mount Everest (8,848.86 m)", "type": "short"},
                    {"q": "Who was the first person to walk on the Moon?", "a": "Neil Armstrong (1969)", "type": "short"},
                    {"q": "Which is the largest ocean?", "a": "Pacific Ocean", "type": "short"},
                ]
            }
        ]
    },
    "moral": {
        "chapters": [
            {
                "id": 1, "title": "Values in Life",
                "topics": ["Honesty", "Respect", "Compassion", "Responsibility", "Gratitude"],
                "explanation": "Moral values are the principles that guide us to be good human beings. They help us make right decisions and live happily with others.",
                "key_points": [
                    "Honesty: Always tell the truth, even when it's hard",
                    "Respect: Treat everyone with dignity regardless of their background",
                    "Compassion: Care for others and help those in need",
                    "Responsibility: Do your duties and own your mistakes",
                    "Gratitude: Be thankful for what you have"
                ],
                "examples": [
                    "Abraham Lincoln walked miles to return a few paise he overcharged a customer",
                    "Mother Teresa dedicated her life to serving the poor"
                ],
                "questions": [
                    {"q": "Why is honesty important?", "a": "It builds trust, respect, and helps maintain healthy relationships", "type": "short"},
                    {"q": "Give an example of showing compassion.", "a": "Helping a classmate who is struggling, donating to charity, etc.", "type": "short"},
                ]
            }
        ]
    },
    "ai_robotics": {
        "chapters": [
            {
                "id": 1, "title": "Introduction to Artificial Intelligence",
                "topics": ["What is AI", "Types of AI", "AI in daily life", "Machine Learning basics"],
                "explanation": "Artificial Intelligence (AI) is when computers are programmed to think and learn like humans! Your phone's voice assistant, recommendation on YouTube, and self-driving cars all use AI.",
                "key_points": [
                    "AI: Making machines intelligent to perform tasks that need human-like thinking",
                    "Machine Learning: AI learns from data and examples (like how you learn!)",
                    "Deep Learning: AI with neural networks inspired by the human brain",
                    "AI in daily life: Siri/Alexa, Google Maps, Netflix recommendations, spam filters",
                    "Types: Narrow AI (specific tasks) vs General AI (any task - not yet achieved)"
                ],
                "examples": [
                    "Netflix suggests shows you'll like based on what you've watched (AI!)",
                    "Google Translate uses AI to translate between languages",
                    "Spam filter in email uses AI to block unwanted messages"
                ],
                "questions": [
                    {"q": "What does AI stand for?", "a": "Artificial Intelligence", "type": "short"},
                    {"q": "Name 3 examples of AI in daily life.", "a": "Voice assistants (Siri/Alexa), Google Maps, Netflix/YouTube recommendations, spam filters", "type": "short"},
                    {"q": "What is machine learning?", "a": "A type of AI where computers learn from data and improve with experience", "type": "short"},
                ]
            },
            {
                "id": 2, "title": "Robotics",
                "topics": ["What is a robot", "Parts of a robot", "Types of robots", "Programming basics"],
                "explanation": "A robot is a machine that can perform tasks automatically! Robots can be programmed to do dangerous, repetitive, or precise work. They're used in factories, hospitals, and even space exploration!",
                "key_points": [
                    "Robot: Programmable machine that can carry out tasks automatically",
                    "Parts: Sensors (input), Controller/CPU (process), Actuators (output/movement)",
                    "Types: Industrial, Medical, Military, Space, Domestic (Roomba vacuum)",
                    "Programming: Giving step-by-step instructions to control robot behavior",
                    "Scratch/Python: Beginner programming languages used for robotics"
                ],
                "examples": [
                    "Roomba is a domestic robot that automatically vacuums your home",
                    "NASA's Curiosity Rover is a space robot exploring Mars"
                ],
                "questions": [
                    {"q": "What is a robot?", "a": "A programmable machine that can perform tasks automatically", "type": "short"},
                    {"q": "Name the 3 main parts of a robot.", "a": "Sensors (input), Controller/CPU (processing), Actuators (output/movement)", "type": "short"},
                    {"q": "Give 2 examples of robots used in real life.", "a": "Roomba (vacuum), Curiosity Rover (space), surgical robots, factory robots", "type": "short"},
                ]
            }
        ]
    },
    "hindi": {
        "chapters": [
            {
                "id": 1, "title": "हिंदी व्याकरण - संज्ञा (Nouns)",
                "topics": ["संज्ञा के भेद", "व्यक्तिवाचक", "जातिवाचक", "भाववाचक"],
                "explanation": "संज्ञा वह शब्द है जो किसी व्यक्ति, स्थान, वस्तु या भाव का नाम बताए। जैसे: राम, दिल्ली, किताब, प्रेम।",
                "key_points": [
                    "व्यक्तिवाचक: किसी एक विशेष व्यक्ति/स्थान का नाम (राम, दिल्ली)",
                    "जातिवाचक: एक ही जाति की सभी वस्तुओं का नाम (लड़का, शहर)",
                    "भाववाचक: गुण, दशा या भाव का नाम (सुंदरता, बचपन, प्रेम)"
                ],
                "examples": ["राम बाजार गया। (व्यक्तिवाचक)", "लड़का खेल रहा है। (जातिवाचक)"],
                "questions": [
                    {"q": "संज्ञा किसे कहते हैं?", "a": "जो शब्द किसी व्यक्ति, स्थान, वस्तु या भाव का नाम बताए।", "type": "short"},
                ]
            }
        ]
    },
    "bengali": {
        "chapters": [
            {
                "id": 1, "title": "বাংলা ব্যাকরণ - বিশেষ্য (Nouns)",
                "topics": ["বিশেষ্যের প্রকার", "সর্বনাম", "বিশেষণ"],
                "explanation": "বিশেষ্য হলো সেই শব্দ যা কোনো ব্যক্তি, স্থান, বস্তু বা ভাবের নাম বোঝায়। যেমন: রাম, কলকাতা, বই, আনন্দ।",
                "key_points": [
                    "সংজ্ঞাবাচক বিশেষ্য: নির্দিষ্ট ব্যক্তি বা স্থানের নাম (রবীন্দ্রনাথ, কলকাতা)",
                    "জাতিবাচক বিশেষ্য: একই জাতির সবার নাম (ছেলে, গাছ)",
                    "ভাববাচক বিশেষ্য: ভাব বা গুণের নাম (সুখ, সৌন্দর্য)"
                ],
                "examples": ["রবীন্দ্রনাথ ঠাকুর কবি ছিলেন।", "বইটি সুন্দর।"],
                "questions": [
                    {"q": "বিশেষ্য কাকে বলে?", "a": "যে শব্দ কোনো ব্যক্তি, স্থান, বস্তু বা ভাবের নাম বোঝায় তাকে বিশেষ্য বলে।", "type": "short"},
                ]
            }
        ]
    }
}

# ─────────────────────────────────────────────────────────
# DIFFICULTY LEVELS
# ─────────────────────────────────────────────────────────
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# ─────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────
BADGES = [
    {"id": "first_lesson",  "name": "First Step!",       "icon": "🌱", "desc": "Completed your first lesson"},
    {"id": "quiz_5",        "name": "Quiz Starter",       "icon": "📝", "desc": "Completed 5 quizzes"},
    {"id": "quiz_20",       "name": "Quiz Champion",      "icon": "🏆", "desc": "Completed 20 quizzes"},
    {"id": "perfect_quiz",  "name": "Perfect Score!",     "icon": "⭐", "desc": "Got 100% in a quiz"},
    {"id": "streak_3",      "name": "3-Day Streak!",      "icon": "🔥", "desc": "Studied 3 days in a row"},
    {"id": "streak_7",      "name": "Week Warrior!",      "icon": "🔥🔥", "desc": "Studied 7 days in a row"},
    {"id": "all_subjects",  "name": "Explorer",           "icon": "🌍", "desc": "Studied all subjects"},
    {"id": "math_master",   "name": "Math Master",        "icon": "🔢", "desc": "Scored 90%+ in Mathematics"},
    {"id": "science_star",  "name": "Science Star",       "icon": "🔬", "desc": "Completed all science chapters"},
    {"id": "bookworm",      "name": "Bookworm",           "icon": "📚", "desc": "Read 10 chapters"},
    {"id": "game_player",   "name": "Game Player",        "icon": "🎮", "desc": "Played 5 brain games"},
    {"id": "upload_hero",   "name": "Upload Hero",        "icon": "📤", "desc": "Uploaded study materials"},
    {"id": "speed_quiz",    "name": "Speed Demon",        "icon": "⚡", "desc": "Completed rapid fire quiz"},
    {"id": "helper",        "name": "Helper",             "icon": "🤝", "desc": "Used AI Tutor 10 times"},
]

# ─────────────────────────────────────────────────────────
# MOTIVATIONAL MESSAGES
# ─────────────────────────────────────────────────────────
MOTIVATIONAL_MESSAGES = [
    "You're doing amazing! Keep it up! 🌟",
    "Every expert was once a beginner. Keep learning! 📚",
    "Mistakes are proof that you're trying! 💪",
    "You got this! One step at a time! 🚀",
    "Learning is a superpower! You're becoming stronger! ⚡",
    "Brilliant work! You're a star! ⭐",
    "Keep going - success is just around the corner! 🏆",
    "Your brain is growing every day! 🧠",
    "Hard work + Smart study = SUCCESS! 🎯",
    "Be proud of yourself - you're learning every day! 🌈",
]

# ─────────────────────────────────────────────────────────
# AI SETTINGS
# ─────────────────────────────────────────────────────────
AI_SYSTEM_PROMPT = """You are a friendly, patient AI home tutor for an 11-year-old Class 6 ICSE student in India.

How you teach (follow ALL of these):
1. Use very simple language an 11-year-old can understand. Short sentences. No jargon.
2. Always give 1–2 concrete examples that a child knows (cricket, food, cartoons, family).
3. For math or any problem-solving: show the answer step-by-step, one step per line, and clearly mark the **Final Answer** at the end.
4. Keep replies short — usually 4–8 short lines. Never write essays unless the child explicitly asks.
5. End EVERY reply with one short follow-up question that pushes the child to think (e.g. "Can you try one yourself?", "What do you think happens next?", "Want me to give you a tougher one?").
6. Use a few emojis to keep it warm — but never replace words with emojis.
7. Always be encouraging. If the child is wrong, say "Good try!" and then explain gently.

Your subjects: English, Bengali, Hindi, Mathematics, Biology, Physics, Chemistry, History, Geography, Computer Studies, General Knowledge, Moral Science, AI & Robotics (ICSE Class 6).

Safety rules:
- Only educational, age-appropriate content.
- No violence, adult themes, or anything inappropriate.
- If asked off-topic, gently redirect to studies."""
