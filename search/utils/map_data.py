import re


def normalize_phone_for_search(s: str) -> str:
    """Return digits-only version of a phone-like string for substring matching."""
    return re.sub(r"\D+", "", s or "")

