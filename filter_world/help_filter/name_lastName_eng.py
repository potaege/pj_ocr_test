import re
from rapidfuzz import process, fuzz

ENG_PREFIXES = ["MR", "MRS", "MS"]

def name_lastname_eng(s: str, prefix_threshold: int = 50):
    
    if not isinstance(s, str):
        return "", "", "", False

    s = s.strip()
    s = re.sub(r"[^A-Za-z\s]", "", s)

    if not s:
        return "", "", "", False

 
    if re.search(r"[A-Za-z]", s) is None:
        return "", "", "", False

    # 2) แยกส่วน
    parts = s.split()
    n = len(parts)

    # ต้องมีอย่างน้อย ชื่อ+นามสกุล
    if n < 2:
        return "", parts[0] if n == 1 else "", "", False

    prefix = ""
    first_name = ""
    last_name = ""

    # 3) ตัดสินคำนำหน้า
    candidate = parts[0]

    if n < 4:
        # ใช้ rapidfuzz ตามที่คุณต้องการ
        match = process.extractOne(candidate, ENG_PREFIXES, scorer=fuzz.ratio)
        # match = (best_string, score, index) หรือ None
        if match is not None:
            best_prefix, score, _ = match
            if score >= prefix_threshold:
                prefix = best_prefix
                remain = parts[1:]
                if len(remain) < 2:
                    return prefix, remain[0] if len(remain) == 1 else "", "", False
                first_name = remain[0]
                last_name = " ".join(remain[1:])
                return prefix, first_name, last_name, True

        # คะแนน < threshold หรือ match ไม่ได้ => ไม่ถือว่าเป็นคำนำหน้า
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        return "", first_name, last_name, True

    else:
        # n >= 4: ตามเงื่อนไขคุณ ไม่ต้อง fuzz
        # ให้ถือว่า prefix เฉพาะกรณีตรงตัว (กันมั่ว)
        if candidate in ENG_PREFIXES:
            prefix = candidate
            remain = parts[1:]
            first_name = remain[0]
            last_name = " ".join(remain[1:])
            return prefix, first_name, last_name, True

        # ไม่ตรงตัว => ไม่ใช้ prefix
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        return "", first_name, last_name, True
