def check_passport_type(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().replace(" ", "").replace(".", "")

    if t in {"P", "D", "O", "ET"}:
        return t, True

    return t, False

# def check_passport_type(text: str, required_len: int):
#     if not isinstance(text, str):
#         return "", False

#     t = text.upper().replace(" ", "").replace(".", "")

#     if len(t) != required_len:
#         return t, False

#     if t in {"P", "D", "O", "ET"}:
#         return t, True

#     return t, False