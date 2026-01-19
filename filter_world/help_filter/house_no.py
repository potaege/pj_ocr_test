import re

HOUSE_ID_PATTERN = re.compile(r"^\d{11}$")

def check_house_no(text: str):

    if not isinstance(text, str):
        return "", False

    raw = text.strip()

    digits = re.sub(r"\D", "", raw)

    if HOUSE_ID_PATTERN.fullmatch(digits):
        return digits, True

    return digits, False
