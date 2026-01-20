from rapidfuzz import process, fuzz
import re

HOUSE_TYPE = {
    "บ้าน",
    "บ้านเดี่ยว",
    "บ้านแฝด",
    "อาคารชุด",
    "ทาวน์เฮาส์",
    "คอนโดมิเนียม",
    "บ้านร้าง",
    "ตึกแถว",
    "เรือนแพ",
    "แฟลต",
    "อื่นๆ"
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

def check_house_type(input_text: str, threshold: int = 50):
    """
    ฟังก์ชันตรวจสอบประเภทบ้าน (House Type)
    เทียบกับ List HOUSE_TYPE ที่กำหนดไว้ข้างบน
    """
    clean_input = _normalize_thai(input_text)
    
    if not clean_input:
        return input_text, False

    choices = list(HOUSE_TYPE)

    # ตรวจสอบคะแนนและคืนค่า
    best_match, score = _best_match(clean_input, choices)
    if best_match and score >= threshold:
        return best_match, True
    else:
        return input_text, False