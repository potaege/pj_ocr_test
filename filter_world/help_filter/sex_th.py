import re

def check_sex_th(text: str):
    if not isinstance(text, str):
        return "", False
    
    t = re.sub(r"^เพศ\s*", "", text.strip())
    t = re.sub(r"\s+", " ", t)

    if t in {"ชาย", "หญิง", "ไม่ระบุ"}:
        return t, True

    return t, False