def check_height(text: str):
    if not isinstance(text, str):
        return "", False

    t = text.upper().strip()

    # Fix OCR common errors
    # t = t.replace(",", ".")
    # t = t.replace("I", "1")

    import re
    pattern = r'^[0-2]\.\d{2}\s?M$'

    if re.match(pattern, t):
        value = float(t.replace("M", "").strip()) # ความสูงประเทศไทยใช้หน่วยเป็นเมตร (M)
        if 0.50 <= value <= 2.50:
            return t, True

    return t, False
