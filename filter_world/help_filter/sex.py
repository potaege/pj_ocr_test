def check_sex(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().replace(" ", "").replace(".", "")

    if t in {"M", "F", "X"}:
        return t, True

    return t, False