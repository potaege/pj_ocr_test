def check_sex_en(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().replace(" ", "").replace(".", "")

    if t in {"M", "F", "X"}:
        return t, True

    return t, False