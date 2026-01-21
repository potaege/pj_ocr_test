import re
from rapidfuzz import fuzz 

PREFIX_LIST = ["หมู่บ้าน", "โครงการ", "ชุมชน", "อาคาร", "บ้าน", "มบ."]

VILLAGE_PREFIX_PATTERN = re.compile(r"(หมู่บ้าน|มบ\.?|บ้าน|ชุมชน|โครงการ|อาคาร)", re.UNICODE)

def fix_village_prefix(text: str, threshold: int = 75) -> str:
    """
    ตรวจสอบและแก้ไขคำนำหน้าชื่อหมู่บ้านถ้ามีความคล้ายคลึงกับ Pattern
    เช่น "ข้าน..." -> "บ้าน...", "หนู่บ้าน..." -> "หมู่บ้าน..."
    """
    if not isinstance(text, str) or not text:
        return text

    for valid_prefix in PREFIX_LIST:
        prefix_len = len(valid_prefix)
        
        # ตัดข้อความ Input มาเฉพาะส่วนหัว ให้ยาวเท่ากับ Prefix ที่จะเทียบ
        if len(text) < prefix_len:
            continue
            
        target_chunk = text[:prefix_len] 

        score = fuzz.ratio(target_chunk, valid_prefix)

        # ถ้าคะแนนสูงพอ (เช่น > 75%) และไม่ใช่คำที่ถูกอยู่แล้ว
        if score >= threshold and score < 100:
            fixed_text = valid_prefix + text[prefix_len:]
            return fixed_text

    return text

def looks_like_village_name(text: str) -> bool:
    if not isinstance(text, str):
        return False
    t = text.strip()
    if VILLAGE_PREFIX_PATTERN.search(t):
        return True
    if re.fullmatch(r"[ก-๙\s]{3,}", t):
        return True
    return False

def char_quality(text: str, min_ratio: float = 0.6) -> bool:
    if not text: return False
    thai_chars = sum(1 for c in text if '\u0E00' <= c <= '\u0E7F')
    return (thai_chars / len(text)) >= min_ratio

def normalize_place_name(text: str) -> str:
    t = text.upper()
    t = re.sub(r"(หมู่บ้าน|มบ\.?|บ้าน|ชุมชน|โครงการ|อาคาร)", "", t)
    t = re.sub(r"\s+", "", t)
    return t

def similarity(a: str, b: str) -> float:
    return fuzz.ratio(a, b) / 100.0

def check_village_name(text: str, reference_names: list[str] | None = None, similarity_threshold: float = 0.75):
    """
    ตรวจสอบชื่อหมู่บ้าน / ชื่อบ้าน
    คืนค่า: (corrected_text, is_valid, status)
    status:
      - 'not_provided'     : ไม่มีข้อมูล (ถือว่า valid)
      - 'matched_reference': match กับ reference
      - 'likely_valid'     : รูปแบบสมเหตุสมผล
      - 'pattern_fail'     : รูปแบบไม่เหมือนชื่อหมู่บ้าน
      - 'low_char_quality' : OCR noise สูง
    """

    if text is None or str(text).strip() == "":
        return "", True, "not_provided"

    if not isinstance(text, str):
        return "", False, "not_string"

    raw = text.strip()

    corrected_text = fix_village_prefix(raw)

    if not looks_like_village_name(corrected_text):
        return corrected_text, False, "pattern_fail"

    if not char_quality(corrected_text):
        return corrected_text, False, "low_char_quality"

    normalized = normalize_place_name(corrected_text)

    if reference_names:
        for ref in reference_names:
            ref_norm = normalize_place_name(ref)
            if similarity(normalized, ref_norm) >= similarity_threshold:
                return corrected_text, True, "matched_reference"

    return corrected_text, True, "likely_valid"