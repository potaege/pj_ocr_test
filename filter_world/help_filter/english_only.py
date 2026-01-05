import re

def keep_english_words(text: str):
   
    if not isinstance(text, str):
        return "", False

    text = text.strip()
    if not text:
        return "", False

    words = text.split()

    eng_words = []
    removed = []

    for w in words:
        # อนุญาตเฉพาะ A-Z a-z และจุด (เผื่อ Mr.)
        if re.fullmatch(r"[A-Za-z\.]+", w):
            eng_words.append(w)
        else:
            removed.append(w)

    clean_text = " ".join(eng_words)

    if not eng_words:
        return "", False

    if removed:
        return clean_text, False

    return clean_text, True
