from rapidfuzz import process, fuzz
import re

VALID_BIRTH_DELIVERY_PERSON = {
    "แพทย์",
    "แพทย์ในโรงพยาบาลรัฐ",
    "แพทย์โรงพยาบาลเอกชน",
    "สูตินรีแพทย์",
    "แพทย์แผนปัจจุบัน",
    "พยาบาล",
    "พยาบาลผดุงครรภ์",
    "พยาบาลวิชาชีพที่มีใบอนุญาตผดุงครรภ์",
    "พบในโรงพยาบาลชุมชน",
    "เจ้าพนักงานสาธารณสุข",
    "เจ้าหน้าที่อนามัย",
    "เจ้าหน้าที่โรงพยาบาลส่งเสริมสุขภาพตำบล",
    "หมอตำแย",
    "ผู้ช่วยทำคลอดแบบดั้งเดิม",
    "พบในอดีตหรือพื้นที่ห่างไกล",
    "บุคคลอื่น",
    "คลอดเอง",
    "อื่นๆ",
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

def check_birth_delivery_person(input_text: str, threshold: int = 50):
    """
    ฟังก์ชันตรวจสอบประเภทผู้ดูแลการคลอด (Birth Delivery Person)
    เทียบกับ List VALID_BIRTH_DELIVERY_PERSON ที่กำหนดไว้ข้างบน
    """
    clean_input = _normalize_thai(input_text)
    
    if not clean_input:
        return input_text, False

    choices = list(VALID_BIRTH_DELIVERY_PERSON)

    # ตรวจสอบคะแนนและคืนค่า
    best_match, score = _best_match(clean_input, choices)
    if best_match and score >= threshold:
        return best_match, True
    else:
        return input_text, False