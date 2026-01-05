def remove_prefix(text: str) -> str:
    if not isinstance(text, str):
        return text
    return text.replace("min general", "").strip()
