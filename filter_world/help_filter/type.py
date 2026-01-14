def check_passport_type(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().replace(" ", "").replace(".", "")

    if t in {"P", "D", "O", "ET"}:
        return t, True

    return t, False