import re

IDENTIFICATION_PATTERN = re.compile(r"^\d{13}$")

def check_identification_no(text: str):

    if not isinstance(text, str):
        return "", False

    raw = text.strip()

    digits = re.sub(r"\D", "", raw)

    if IDENTIFICATION_PATTERN.fullmatch(digits):
        return digits, True

    return digits, False
