"""
src/core/validators.py — Input validation helpers.
"""
from __future__ import annotations


class ValidationError(ValueError):
    pass


def validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValidationError("Name cannot be empty.")
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters.")
    if len(name) > 50:
        raise ValidationError("Name must be 50 characters or fewer.")
    return name.title()


def validate_weight_kg(value: str) -> float:
    try:
        w = float(value)
    except ValueError:
        raise ValidationError("Weight must be a number.")
    if not (1 <= w <= 600):
        raise ValidationError("Weight must be between 1 and 600 kg.")
    return w


def validate_weight_lbs(value: str) -> float:
    try:
        w = float(value)
    except ValueError:
        raise ValidationError("Weight must be a number.")
    if not (2 <= w <= 1320):
        raise ValidationError("Weight must be between 2 and 1320 lbs.")
    return w


def validate_height_cm(value: str) -> float:
    try:
        h = float(value)
    except ValueError:
        raise ValidationError("Height must be a number.")
    if not (50 <= h <= 300):
        raise ValidationError("Height must be between 50 and 300 cm.")
    return h


def validate_height_feet(ft_str: str, in_str: str) -> tuple[float, float]:
    try:
        ft = float(ft_str)
    except ValueError:
        raise ValidationError("Feet must be a number.")
    try:
        ins = float(in_str) if in_str.strip() else 0.0
    except ValueError:
        raise ValidationError("Inches must be a number.")
    if not (1 <= ft <= 9):
        raise ValidationError("Feet must be between 1 and 9.")
    if not (0 <= ins < 12):
        raise ValidationError("Inches must be between 0 and 11.")
    return ft, ins
