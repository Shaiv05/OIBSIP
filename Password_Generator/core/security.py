"""Security analysis: strength scoring, entropy, warnings."""

import math
import re
import string


STRENGTH_LEVELS = {
    "Very Weak": {"color": "#ef4444", "bar": 0.1},
    "Weak":      {"color": "#f97316", "bar": 0.3},
    "Fair":      {"color": "#eab308", "bar": 0.5},
    "Strong":    {"color": "#22c55e", "bar": 0.75},
    "Very Strong": {"color": "#10b981", "bar": 1.0},
}


def analyze_password(password: str, charset_size: int = 72) -> dict:
    if not password:
        return {
            "strength": "Very Weak",
            "score": 0,
            "entropy_bits": 0.0,
            "crack_time": "instant",
            "warnings": ["No password generated."],
            "color": "#ef4444",
            "bar_fraction": 0.0,
        }

    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    # Estimate effective charset from password content
    effective_charset = 0
    if has_upper:
        effective_charset += 26
    if has_lower:
        effective_charset += 26
    if has_digit:
        effective_charset += 10
    if has_symbol:
        effective_charset += 32
    if effective_charset == 0:
        effective_charset = 10

    entropy_bits = length * math.log2(effective_charset)

    score = _compute_score(length, entropy_bits, has_upper, has_lower, has_digit, has_symbol, password)
    strength = _score_to_strength(score)
    warnings = _build_warnings(length, has_upper, has_lower, has_digit, has_symbol, entropy_bits, password)
    crack_time = _estimate_crack_time(entropy_bits)

    return {
        "strength": strength,
        "score": score,
        "entropy_bits": round(entropy_bits, 1),
        "crack_time": crack_time,
        "warnings": warnings,
        "color": STRENGTH_LEVELS[strength]["color"],
        "bar_fraction": STRENGTH_LEVELS[strength]["bar"],
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "length": length,
    }


def _compute_score(length, entropy, upper, lower, digit, symbol, password) -> int:
    score = 0

    # Length scoring
    if length >= 8:
        score += 10
    if length >= 12:
        score += 15
    if length >= 16:
        score += 20
    if length >= 24:
        score += 10

    # Entropy scoring
    if entropy >= 40:
        score += 10
    if entropy >= 60:
        score += 15
    if entropy >= 80:
        score += 15
    if entropy >= 100:
        score += 10

    # Character type diversity
    types = sum([upper, lower, digit, symbol])
    score += types * 5

    # Penalize repetition
    if re.search(r"(.)\1{2,}", password):
        score -= 10

    # Penalize sequential
    seq_count = sum(
        1 for i in range(len(password) - 2)
        if ord(password[i + 1]) - ord(password[i]) == 1
        and ord(password[i + 2]) - ord(password[i + 1]) == 1
    )
    score -= seq_count * 3

    return max(0, min(score, 100))


def _score_to_strength(score: int) -> str:
    if score < 15:
        return "Very Weak"
    elif score < 35:
        return "Weak"
    elif score < 55:
        return "Fair"
    elif score < 75:
        return "Strong"
    else:
        return "Very Strong"


def _build_warnings(length, upper, lower, digit, symbol, entropy, password) -> list:
    warnings = []
    if length < 8:
        warnings.append("Password is too short (minimum 8 characters).")
    if length < 12:
        warnings.append("Consider using at least 12 characters for better security.")
    if not upper:
        warnings.append("No uppercase letters — reduces strength.")
    if not lower:
        warnings.append("No lowercase letters — reduces strength.")
    if not digit:
        warnings.append("No digits — reduces character variety.")
    if not symbol:
        warnings.append("No symbols — consider adding them for stronger passwords.")
    if entropy < 40:
        warnings.append("Low entropy — password is guessable.")
    if re.search(r"(.)\1{3,}", password):
        warnings.append("Contains repeated characters — avoid predictable patterns.")
    if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg)", password.lower()):
        warnings.append("Contains sequential pattern — avoid sequences.")
    return warnings


def _estimate_crack_time(entropy_bits: float) -> str:
    """Estimate crack time assuming 10 billion guesses/second (GPU cluster)."""
    guesses_per_second = 1e10
    combinations = 2 ** entropy_bits
    seconds = combinations / guesses_per_second

    if seconds < 1:
        return "less than a second"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 3.154e9:
        return f"{int(seconds / 31536000)} years"
    elif seconds < 3.154e12:
        return f"{int(seconds / 3.154e9)} thousand years"
    elif seconds < 3.154e15:
        return f"{int(seconds / 3.154e12)} million years"
    else:
        return "billions of years"
