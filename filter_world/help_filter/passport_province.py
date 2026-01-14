from rapidfuzz import process, fuzz
import re

def _best_match(text: str, choices: list[str]):
    """
    ค้นหาคำที่เหมือนที่สุดจากรายการ choices
    คืนค่า: (คำที่แมตช์ได้, คะแนนความเหมือน)
    """
    if not choices:
        return None, 0
    res = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    if not res:
        return None, 0
    best, score, _ = res
    return best, score

def _normalize_english(text: str) -> str:
    """
    เตรียมข้อความภาษาอังกฤษ:
    - แปลงเป็นตัวพิมพ์ใหญ่ (UPPERCASE)
    - เก็บเฉพาะ A-Z, 0-9 และช่องว่าง
    - ตัดหัวท้ายและยุบช่องว่างที่ซ้ำกัน
    """
    if not isinstance(text, str):
        return ""
    
    text = text.upper()
    
    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_province_en(input_text: str, provinces_data: dict, threshold: int = 30):
    clean_input = _normalize_english(input_text)

    if not clean_input:
        return None, False

    # เตรียม Choice จาก provinces_data ที่ส่งเข้ามา
    prov_choices: list[str] = []
    prov_upper_to_original: dict[str, str] = {} 

    # วนลูปดึงข้อมูลจาก Dict ที่รับเข้ามา
    for prov_code, obj in provinces_data.items():
        name_en = str(obj.get("name_en", "")).strip()
        
        if name_en:
            name_en_upper = _normalize_english(name_en)
            
            if name_en_upper:
                prov_choices.append(name_en_upper)
                
                prov_upper_to_original[name_en_upper] = name_en_upper 

    best_match_upper, score = _best_match(clean_input, prov_choices)

    # ตรวจสอบคะแนนและคืนค่า
    if best_match_upper and score >= threshold:
        result_name = prov_upper_to_original.get(best_match_upper, best_match_upper)
        return result_name, True
    else:
        return None, False