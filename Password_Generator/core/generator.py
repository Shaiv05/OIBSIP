"""Password and passphrase generation using Python's secrets module."""

import secrets
import string
import math
import re

SIMILAR_CHARS = set("O0Il1")
AMBIGUOUS_SYMBOLS = set('{}[]()/\\\'"`~,;:.<>')

WORDLIST = [
    "apple", "brave", "cloud", "dance", "eagle", "flame", "grace", "haven",
    "indie", "jewel", "kites", "lemon", "maple", "noble", "ocean", "prism",
    "quiet", "river", "stone", "tiger", "ultra", "vivid", "wheat", "xenon",
    "yield", "zesty", "blaze", "crisp", "drift", "ember", "frost", "glide",
    "haste", "ivory", "jazzy", "knack", "lunar", "misty", "nifty", "optic",
    "plume", "quirk", "rainy", "swift", "thorn", "unity", "vapor", "wrath",
    "xtend", "young", "zonal", "amber", "bloom", "cedar", "dusty", "elfin",
    "flint", "grove", "honey", "inlet", "joust", "kudos", "lofty", "magic",
    "night", "onyx", "petal", "quest", "ridge", "solar", "trout", "umbra",
    "vibes", "windy", "xerox", "yarns", "zeros", "agile", "bison", "comet",
    "delta", "elite", "flair", "gleam", "hippo", "irony", "joker", "karma",
    "lyric", "mount", "ninja", "orbit", "pixel", "quill", "rapid", "sigma",
    "titan", "urban", "value", "waves", "xeric", "yacht", "zonal",
]


def build_charset(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_similar: bool,
    exclude_ambiguous: bool,
    exclude_custom: str,
) -> str:
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        syms = string.punctuation
        if exclude_ambiguous:
            syms = "".join(c for c in syms if c not in AMBIGUOUS_SYMBOLS)
        chars += syms

    if exclude_similar:
        chars = "".join(c for c in chars if c not in SIMILAR_CHARS)

    if exclude_custom:
        excluded = set(exclude_custom)
        chars = "".join(c for c in chars if c not in excluded)

    return chars


def _mandatory_chars(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_similar: bool,
    exclude_ambiguous: bool,
    exclude_custom: str,
) -> list:
    """Return one guaranteed character from each enabled category."""
    mandatory = []
    excluded_custom = set(exclude_custom)

    def pick_from(pool: str) -> str | None:
        filtered = "".join(
            c for c in pool
            if (not exclude_similar or c not in SIMILAR_CHARS)
            and c not in excluded_custom
        )
        return secrets.choice(filtered) if filtered else None

    if use_upper:
        c = pick_from(string.ascii_uppercase)
        if c:
            mandatory.append(c)
    if use_lower:
        c = pick_from(string.ascii_lowercase)
        if c:
            mandatory.append(c)
    if use_digits:
        c = pick_from(string.digits)
        if c:
            mandatory.append(c)
    if use_symbols:
        syms = string.punctuation
        if exclude_ambiguous:
            syms = "".join(c for c in syms if c not in AMBIGUOUS_SYMBOLS)
        c = pick_from(syms)
        if c:
            mandatory.append(c)

    return mandatory


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_similar: bool = False,
    exclude_ambiguous: bool = False,
    exclude_custom: str = "",
    no_consecutive_repeats: bool = False,
    avoid_patterns: bool = False,
) -> str:
    charset = build_charset(
        use_upper, use_lower, use_digits, use_symbols,
        exclude_similar, exclude_ambiguous, exclude_custom,
    )
    if not charset:
        raise ValueError("No characters available with current settings.")

    mandatory = _mandatory_chars(
        use_upper, use_lower, use_digits, use_symbols,
        exclude_similar, exclude_ambiguous, exclude_custom,
    )

    if length < len(mandatory):
        raise ValueError(
            f"Password length must be at least {len(mandatory)} to satisfy all enabled character types."
        )

    remaining_length = length - len(mandatory)
    password_chars = list(mandatory)

    for _ in range(remaining_length):
        if no_consecutive_repeats and password_chars:
            pool = [c for c in charset if c != password_chars[-1]]
            if not pool:
                pool = list(charset)
            password_chars.append(secrets.choice(pool))
        else:
            password_chars.append(secrets.choice(charset))

    # Shuffle to remove positional bias from mandatory chars
    secrets.SystemRandom().shuffle(password_chars)

    password = "".join(password_chars)

    if avoid_patterns:
        password = _break_patterns(password, charset)

    return password


def _break_patterns(password: str, charset: str) -> str:
    """Replace characters that form obvious keyboard/sequential patterns."""
    sequential_runs = re.compile(r"(.)\1{2,}")
    result = list(password)
    for match in sequential_runs.finditer(password):
        start = match.start() + 2
        for i in range(start, match.end()):
            replacement = secrets.choice(charset)
            attempts = 0
            while replacement == result[i - 1] and attempts < 10:
                replacement = secrets.choice(charset)
                attempts += 1
            result[i] = replacement
    return "".join(result)


def generate_passphrase(
    word_count: int = 4,
    separator: str = "-",
    capitalize: bool = True,
    add_number: bool = True,
    add_symbol: bool = False,
) -> str:
    words = [secrets.choice(WORDLIST) for _ in range(word_count)]
    if capitalize:
        words = [w.capitalize() for w in words]

    parts = list(words)
    if add_number:
        parts.append(str(secrets.randbelow(9000) + 1000))
    if add_symbol:
        safe_symbols = "!@#$%^&*"
        parts.append(secrets.choice(safe_symbols))

    return separator.join(parts)


def calculate_entropy(password: str) -> float:
    """Calculate Shannon entropy of the password."""
    if not password:
        return 0.0
    from collections import Counter
    freq = Counter(password)
    length = len(password)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )
    return round(entropy * length, 2)


def estimate_charset_size(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_similar: bool,
    exclude_ambiguous: bool,
) -> int:
    size = 0
    if use_upper:
        size += 26 - (len([c for c in SIMILAR_CHARS if c.isupper()]) if exclude_similar else 0)
    if use_lower:
        size += 26 - (len([c for c in SIMILAR_CHARS if c.islower()]) if exclude_similar else 0)
    if use_digits:
        size += 10 - (len([c for c in SIMILAR_CHARS if c.isdigit()]) if exclude_similar else 0)
    if use_symbols:
        base = len(string.punctuation)
        if exclude_ambiguous:
            base -= len(AMBIGUOUS_SYMBOLS)
        size += base
    return max(size, 1)
