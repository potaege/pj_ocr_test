from rapidfuzz import process, fuzz
import re

HOUSE_SPECIFICATION = {
    "บ้าน",
    "บ้านเดี่ยว",
    "ตึกเดี่ยว 1 ชั้น",
    "ตึกเดี่ยว 2 ชั้น",
    "ตึกเดี่ยว 3 ชั้น",
    "ตึกเดี่ยว 4 ชั้น",
    "ตึกเดี่ยว 5 ชั้น",
    "ตึกเดี่ยว 6 ชั้น",
    "บ้านแฝด",
    "ตึกแฝด 1 ชั้น",
    "ตึกแฝด 2 ชั้น",
    "ตึกแฝด 3 ชั้น",
    "ตึกแฝด 4 ชั้น",
    "ตึกแฝด 5 ชั้น",
    "ตึกแฝด 6 ชั้น",
    "อาคารชุด",
    "ทาวน์เฮาส์",
    "คอนโดมิเนียม",
    "บ้านร้าง",
    "ตึกแถว",
    "ตึกเดี่ยว",
    "ตึกแฝด",
}

def _best_match(text: str, choices: list[str]):
    """
    ค้นหาคำที่เหมือนที่สุดจากรายการ choices
    """
    if not choices:
        return None, 0
    res = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    if not res:
        return None, 0
    best, score, _ = res
    return best, score

def _normalize_thai(text: str) -> str:
    """
    ล้างข้อความ: เก็บเฉพาะภาษาไทย (ก-๙), ตัวเลข, และช่องว่าง
    """
    if not isinstance(text, str):
        return ""
    
    text = re.sub(r"[^ก-๙๐-๙0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def check_house_specification(input_text: str, threshold: int = 50):
    """
    ฟังก์ชันตรวจสอบประเภทบ้าน (House Specification)
    เทียบกับ List HOUSE_SPECIFICATION ที่กำหนดไว้ข้างบน
    """
    clean_input = _normalize_thai(input_text)
    
    if not clean_input:
        return input_text, False

    choices = list(HOUSE_SPECIFICATION)

    # ตรวจสอบคะแนนและคืนค่า
    best_match, score = _best_match(clean_input, choices)
    if best_match and score >= threshold:
        return best_match, True
    else:
        return input_text, False