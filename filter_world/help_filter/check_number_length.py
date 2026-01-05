def check_number_length(text: str, required_len: int):
    if not isinstance(text, str):
        return "", False, "not_string"

    digits = "".join(ch for ch in text if ch.isdigit())

    if len(digits) < required_len:
        return digits, False

    return digits[:required_len], True
