"""
config.py — App-wide configuration and constants.
"""
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data_store")
DATA_FILE  = os.path.join(DATA_DIR, "bmi_data.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# ── App meta ───────────────────────────────────────────────────────────────────
APP_NAME    = "BMI Tracker Pro"
APP_VERSION = "2.0.0"
WINDOW_SIZE = "960x920"

# ── BMI categories  ──────────────────────────────────────────────────────────
# Each tuple: (upper_limit, label, hex_color, emoji)
BMI_CATEGORIES = [
    (16.0,       "Severely Underweight", "#e74c3c", "⚠️"),
    (18.5,       "Underweight",          "#e67e22", "⚡"),
    (25.0,       "Normal Weight",        "#2ecc71", "✅"),
    (30.0,       "Overweight",           "#f39c12", "⚡"),
    (35.0,       "Obese Class I",        "#e74c3c", "⚠️"),
    (40.0,       "Obese Class II",       "#c0392b", "⚠️"),
    (float("inf"), "Obese Class III",    "#922b21", "🚨"),
]

# ── Health tips per category ──────────────────────────────────────────────────
HEALTH_TIPS = {
    "Severely Underweight": [
        "Consult a healthcare provider immediately.",
        "Focus on calorie-dense, nutrient-rich foods.",
        "Consider working with a registered dietitian.",
    ],
    "Underweight": [
        "Increase caloric intake with healthy foods.",
        "Add strength training to build muscle mass.",
        "Eat more frequently — 5–6 small meals a day.",
    ],
    "Normal Weight": [
        "Great job! Maintain your healthy lifestyle.",
        "Keep up regular physical activity (150 min/week).",
        "Stay hydrated and prioritize sleep.",
    ],
    "Overweight": [
        "Reduce processed foods and added sugars.",
        "Aim for 30 min of moderate activity daily.",
        "Track meals to stay within calorie goals.",
    ],
    "Obese Class I": [
        "Consult a doctor for a personalised plan.",
        "Start with low-impact exercise (walking, swimming).",
        "Focus on sustainable lifestyle changes, not crash diets.",
    ],
    "Obese Class II": [
        "Medical supervision is strongly recommended.",
        "Small changes add up — even 5% weight loss helps.",
        "Look into structured weight-management programmes.",
    ],
    "Obese Class III": [
        "Please seek medical advice promptly.",
        "Bariatric options may be worth discussing with a doctor.",
        "Every step counts — begin with small, daily walks.",
    ],
}

# ── Theme colours ─────────────────────────────────────────────────────────────
THEME = {
    "bg":          "#0f1117",   # near-black background
    "surface":     "#1a1d2e",   # card surface
    "surface2":    "#252840",   # slightly lighter surface
    "accent":      "#4f8ef7",   # primary blue accent
    "accent2":     "#7c6af7",   # purple accent
    "success":     "#2ecc71",
    "warning":     "#f39c12",
    "danger":      "#e74c3c",
    "text":        "#e8eaf6",
    "text_muted":  "#7986cb",
    "border":      "#2d3154",
    "entry_bg":    "#1e2235",
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_FAMILY   = "Helvetica"
FONT_MONO     = "Courier"
