def check_country_code(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().replace(" ", "").replace(".", "")

    if t == "THA":
        return t, True

    return t, False