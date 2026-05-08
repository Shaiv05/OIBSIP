"""
src/core/calculator.py — Pure BMI calculation logic (no UI dependencies).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import BMI_CATEGORIES, HEALTH_TIPS


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class BMIRecord:
    user: str
    weight_kg: float
    height_cm: float
    bmi: float
    category: str
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    unit_system: str = "metric"   # "metric" | "imperial"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "BMIRecord":
        # Be lenient — old records may lack new fields
        return cls(
            user        = d.get("user", "Unknown"),
            weight_kg   = float(d.get("weight_kg", 0)),
            height_cm   = float(d.get("height_cm", 0)),
            bmi         = float(d.get("bmi", 0)),
            category    = d.get("category", "Unknown"),
            date        = d.get("date", ""),
            unit_system = d.get("unit_system", "metric"),
            notes       = d.get("notes", ""),
        )


# ── Calculation helpers ───────────────────────────────────────────────────────

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Return BMI rounded to 2 decimal places."""
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")
    return round(weight_kg / ((height_cm / 100.0) ** 2), 2)


def get_category(bmi: float) -> tuple[str, str, str]:
    """Return (label, hex_colour, emoji) for a given BMI value."""
    for upper, label, colour, emoji in BMI_CATEGORIES:
        if bmi < upper:
            return label, colour, emoji
    return "Unknown", "#ffffff", "❓"


def get_health_tips(category: str) -> list[str]:
    return HEALTH_TIPS.get(category, ["Consult a healthcare professional."])


def ideal_weight_range(height_cm: float) -> tuple[float, float]:
    """Return (min_kg, max_kg) for BMI 18.5–25 at given height."""
    h_m = height_cm / 100.0
    return round(18.5 * h_m ** 2, 1), round(24.9 * h_m ** 2, 1)


# ── Unit conversions ──────────────────────────────────────────────────────────

def lbs_to_kg(lbs: float) -> float:
    return round(lbs * 0.453592, 2)


def kg_to_lbs(kg: float) -> float:
    return round(kg / 0.453592, 2)


def inches_to_cm(inches: float) -> float:
    return round(inches * 2.54, 2)


def cm_to_inches(cm: float) -> float:
    return round(cm / 2.54, 2)


def feet_inches_to_cm(feet: float, inches: float) -> float:
    total_inches = feet * 12 + inches
    return inches_to_cm(total_inches)


# ── Stats helpers ─────────────────────────────────────────────────────────────

def compute_stats(records: list[BMIRecord]) -> Optional[dict]:
    if not records:
        return None

    bmis = [r.bmi for r in records]
    categories: dict[str, int] = {}
    for r in records:
        categories[r.category] = categories.get(r.category, 0) + 1

    return {
        "count":      len(records),
        "average":    round(sum(bmis) / len(bmis), 2),
        "lowest":     min(bmis),
        "highest":    max(bmis),
        "categories": categories,
        "trend":      bmis[-1] - bmis[-2] if len(bmis) >= 2 else None,
    }
