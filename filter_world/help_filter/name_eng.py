import re

ENG_PREFIXES = [
    "Mr.", "Mrs.", "Ms.", "Miss", "Dr.", "Prof.",
    "MR.", "MRS.", "MS.", "MISS", "DR.", "PROF."
]

def split_name_eng(s: str):
    
    if not isinstance(s, str):
        return "", "", False

    s = s.strip()
    if not s:
        return "", "", False

    s = re.sub(r"[^A-Za-z\.\s]", " ", s)

    # normalize space
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return "", "", False

    parts = s.split()

    # 2) มีแค่คำเดียว -> ไม่มี prefix
    if len(parts) == 1:
        return "", parts[0], True

    # 3) ตรวจ prefix
    candidate = parts[0]

    if candidate in ENG_PREFIXES:
        first_name = parts[1]
        return candidate, first_name, True

    # 4) ไม่ตรง prefix แต่มีหลายคำ
    # ถือว่าเป็นชื่อทั้งหมด (กัน OCR เพี้ยน)
    return "", parts[0], True
