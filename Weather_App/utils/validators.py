"""Input validation helpers."""

import re


def validate_location(value: str) -> tuple[bool, str]:
    """Validate a user-entered location before any API call."""
    location = (value or "").strip()
    if not location:
        return False, "Enter a location before searching."
    if len(location) < 2:
        return False, "Location must be at least 2 characters."
    if len(location) > 100:
        return False, "Location is too long."
    if re.search(r"https?://|www\.|[@#$%^*_={}\\[\\]<>|~`]", location, re.IGNORECASE):
        return False, "Enter a city, state, region, or country name only."
    if not re.search(r"[a-zA-Z]", location):
        return False, "Location must contain at least one letter."
    if not re.match(r"^[a-zA-Z0-9\s,.'\-]+$", location):
        return False, "Location contains invalid characters."
    return True, ""
