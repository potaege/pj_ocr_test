from rapidfuzz import process, fuzz
import re

def _best_match(text: str, choices: list[str]):
    if not choices:
        return None, 0
    res = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    if not res:
        return None, 0
    best, score, _ = res
    return best, score

def _normalize_thai(text: str) -> str:
    if not isinstance(text, str):
        return ""
    
    # เก็บเฉพาะภาษาไทย (ก-๙), ตัวเลข, และช่องว่าง
    text = re.sub(r"[^ก-๙๐-๙0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_registry_office(input_text: str, office_data: dict, threshold: int = 30):
    clean_input = _normalize_thai(input_text)
    
    if not clean_input:
        return input_text, False
    
    # เตรียม Choice จาก registration_offices_data ที่ส่งเข้ามา
    compare_choices = []
    short_to_full_map = {}
    
    for key, info in office_data.items():
        full_name = str(info.get("offices", "")).strip()
        
        if full_name:
            compare_name = full_name.replace("สำนักทะเบียน", "").strip()
            
            if compare_name:
                compare_choices.append(compare_name)
                short_to_full_map[compare_name] = full_name

    best_match_short, score = _best_match(clean_input, compare_choices)

    if best_match_short and score >= threshold:
        full_correct_name = short_to_full_map.get(best_match_short, best_match_short)
        full_correct_name = full_correct_name.replace("สำนักทะเบียน", "").strip()
        return full_correct_name, True
    else:
        return input_text, False