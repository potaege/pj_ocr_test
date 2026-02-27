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

def _normalize_thai(text: str) -> str:
    """
    เตรียมข้อความภาษาไทย:
    - เก็บเฉพาะภาษาไทย (ก-๙), ตัวเลขไทย/อารบิก และช่องว่าง
    - ตัดสัญลักษณ์พิเศษและภาษาอังกฤษทิ้ง
    - ตัดหัวท้ายและยุบช่องว่างที่ซ้ำกัน
    """
    if not isinstance(text, str):
        return ""
    
    # อนุญาตเฉพาะตัวอักษรไทย ตัวเลข และช่องว่าง
    text = re.sub(r"[^ก-ฮะ-์\s]", " ", text)
    
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_province_th(input_text: str, provinces_data: dict, threshold: int = 50):
    clean_input = _normalize_thai(input_text)

    if not clean_input:
        return input_text, False

    # เตรียม Choice จาก provinces_data ที่ส่งเข้ามา
    prov_choices: list[str] = []
    prov_clean_to_original: dict[str, str] = {} 

    # วนลูปดึงข้อมูลจาก Dict ที่รับเข้ามา
    for prov_code, obj in provinces_data.items():
        name_th = str(obj.get("name", "")).strip()
        
        if name_th:
            name_th_clean = _normalize_thai(name_th)
            
            if name_th_clean:
                prov_choices.append(name_th_clean)
                
                prov_clean_to_original[name_th_clean] = name_th 

    best_match_clean, score = _best_match(clean_input, prov_choices)

    # ตรวจสอบคะแนนและคืนค่า
    if best_match_clean and score >= threshold:
        result_name = prov_clean_to_original.get(best_match_clean, best_match_clean)
        return result_name, True
    else:
        return input_text, False