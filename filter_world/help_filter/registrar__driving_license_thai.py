import re
from rapidfuzz import process, fuzz

def find_province_from_registrar(registrar_text: str, provinces: dict, threshold: int = 40):
    # clean OCR (เก็บไทย/อังกฤษ/เลข/ช่องว่าง)
    s = re.sub(r"[^ก-๙A-Za-z0-9\s]", "", registrar_text)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return None , None, 0, [], False

    
    nums = re.findall(r"\d+", s)

    # === แยก list ไทย / อังกฤษ ===
    th_choices: list[str] = []
    en_choices: list[str] = []

    for _, obj in provinces.items():
        name_th = (obj.get("name_th") or "").strip()
        name_en = (obj.get("name_en") or "").strip()
        if name_th:
            th_choices.append(name_th)
        if name_en:
            en_choices.append(name_en)

    # match ไทย
    s_thai = re.sub(r"[^ก-ฮ\s]", "", s)
    
    th_match = process.extractOne(s_thai, th_choices, scorer=fuzz.token_set_ratio) if th_choices else None
    # match อังกฤษ
    s_eng = re.sub(r"[^A-Za-z\s]", "", s)
    en_match = process.extractOne(s_eng, en_choices, scorer=fuzz.token_set_ratio) if en_choices else None

    best = None  

    if th_match:
        name, score, _ = th_match
        best = (name, score, "th")

    if en_match:
        name, score, _ = en_match
        if best is None or score > best[1]:
            best = (name, score, "en")

    if best is None or best[1] < threshold:
        return None ,None , best[1] if best else 0,  nums, False

    if best[2] == "th":
        idx = th_choices.index(name)

        outpue_name_th = name
        output_name_eng = en_choices[idx]
    else:
        idx = en_choices.index(name)

        outpue_name_th = th_choices[idx]
        output_name_eng = name

    return outpue_name_th, output_name_eng , score, nums, True
