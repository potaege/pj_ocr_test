import re
from rapidfuzz import process, fuzz

# รายการศาสนาที่พบบ่อยในงานเอกสารไทย (ปรับเพิ่ม/ลดได้ตามข้อมูลจริงของคุณ)
THAI_RELIGIONS = [
    "พุทธ",
    "อิสลาม",
    "คริสต์",
    "ฮินดู",
    "ซิกข์",
    "ไม่ระบุ",
    "ไม่มีศาสนา",
    "-",  # บางชุดข้อมูลอาจเป็นขีด
]

def normalize_religion_th(text: str, threshold: int = 50):
    
    if not isinstance(text, str):
        return "", False, "not_string", 0, ""

    s = text.strip()
    if not s:
        return "", False, "empty", 0, ""

    # 1) ตรวจว่าเป็นภาษาไทยล้วน (อนุญาต ช่องว่าง และ จุด และ ขีด)
    # ถ้าคุณ "ต้องการไทยล้วน 100%" จริง ๆ ให้ใช้ pattern นี้
    if re.fullmatch(r"[ก-๙\s\.\-]+", s) is None:
        return "", False, "not_thai_only", 0, ""

    # 2) fuzzy match
    match = process.extractOne(s, THAI_RELIGIONS, scorer=fuzz.ratio)
    if match is None:
        return "", False

    best, score, _ = match

    # 3) ตัดสินผ่าน/ไม่ผ่าน
    if score < threshold:
        # คืนค่าต้นฉบับไว้ เผื่อ debug แต่บอกว่าไม่ผ่าน
        return "", True

    return best, True
