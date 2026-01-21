import re

ALLOWED_PATTERN = re.compile(r"^[A-Za-zก-๙0-9\s]{2,}$")

FORBIDDEN_PATTERN = re.compile(r"[^\wก-๙\s]")

def check_house_name(text: str):
    """
    return: (normalized_value, is_valid, status)
    """
    if not text or not isinstance(text, str):
        return "", True, "not_provided"

    raw = text.strip()

    if FORBIDDEN_PATTERN.search(raw):
        return raw, False, "contains_symbol"

    if not ALLOWED_PATTERN.fullmatch(raw):
        return raw, False, "invalid_charset"

    core = raw.replace(" ", "")
    if len(core) < 2:
        return raw, False, "too_short"

    # Language + number ratio
    valid_chars = sum(
        1 for c in core
        if (
            ('\u0E00' <= c <= '\u0E7F') or
            ('A' <= c <= 'Z') or
            ('a' <= c <= 'z') or
            ('0' <= c <= '9')
        )
    )

    if valid_chars / len(core) < 0.7:
        return raw, False, "low_valid_ratio"
    normalized = re.sub(r"\s+", " ", raw)

    return normalized, True, "likely_house_name"