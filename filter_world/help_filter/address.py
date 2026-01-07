from rapidfuzz import process, fuzz
import re


def _best_match(text: str, choices: list[str]):
    if not choices:
        return None, 0
    res = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    if res is None:
        return None, 0
    best, score, _ = res
    return best, score


def _remove_once(full_text: str, piece: str) -> str:
    if not piece:
        return full_text
    return full_text.replace(piece, "", 1).strip()


def _keep_thai_digits(text: str) -> str:
    text = re.sub(r"[^0-9ก-๙\s\/\-\.\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _remove_address_word(text: str) -> str:
    text = re.sub(r"^\s*ที่อยู่\s*[:\-]?\s*", "", text).strip()
    return text


def _find_by_containment(text: str, choices: list[str]):
    hits = [c for c in choices if c and c in text]
    if not hits:
        return None, 0
    hits.sort(key=len, reverse=True)
    return hits[0], 100


def _extract_after_keyword(text: str, keywords: tuple[str, ...], stop_words: tuple[str, ...]) -> str:
    kw_pattern = "(" + "|".join(map(re.escape, keywords)) + r")\s*"
    m = re.search(kw_pattern + r"([ก-๙]+)", text)
    if not m:
        return ""
    candidate = m.group(2).strip()
    return candidate


# ✅ NEW: ตัดเอาแค่ก่อนคำว่า แขวง/ตำบล/เขต/อำเภอ/จังหวัด/ชื่อจังหวัด
def _cut_before_admin(text: str, province_th: str = "") -> str:
    markers = ["แขวง", "ตำบล", "เขต", "อำเภอ", "จังหวัด"]
    if province_th:
        markers.append(province_th)

    idxs = [text.find(m) for m in markers if m and text.find(m) != -1]
    if not idxs:
        return text.strip()
    cut = min(idxs)
    return text[:cut].strip()


def parse_admin_from_address(
    address_text: str,
    provinces: dict,
    districts: dict,
    sub_districts: dict,
    province_threshold: int = 40,
    district_threshold: int = 40,
    subdistrict_threshold: int = 40
):
    status = True

    if not isinstance(address_text, str) or not address_text.strip():
        return "", "", "", "", False

    # ---------- 0) preprocess ----------
    text = _remove_address_word(_keep_thai_digits(address_text.strip()))

    # ---------- 1) Province ----------
    prov_choices = []
    prov_name_to_code = {}

    for prov_code, obj in provinces.items():
        name_th = (obj.get("name_th") or "").strip()
        if name_th:
            prov_choices.append(name_th)
            prov_name_to_code[name_th] = prov_code

    best_prov, prov_score = _find_by_containment(text, prov_choices)
    if not best_prov:
        best_prov, prov_score = _best_match(text, prov_choices)

    if not best_prov or prov_score < province_threshold:
        status = False

    prov_code = prov_name_to_code.get(best_prov, "")
    province_th = best_prov or ""

    # ---------- 2) District (within province) ----------
    district_th = ""
    dist_code = ""

    if prov_code and prov_code in districts:
        prov_districts = districts.get(prov_code, {})

        dist_choices = []
        dist_name_to_code = {}

        for d_code, d_obj in prov_districts.items():
            if isinstance(d_obj, dict):
                d_name = (d_obj.get("name_th") or "").strip()
            else:
                d_name = (str(d_obj) or "").strip()

            if d_name:
                dist_choices.append(d_name)
                dist_name_to_code[d_name] = d_code

        dist_hint = _extract_after_keyword(
            text, keywords=("เขต", "อำเภอ"), stop_words=("แขวง", "ตำบล", "จังหวัด")
        )

        best_dist, dist_score = _find_by_containment(dist_hint or text, dist_choices)
        if not best_dist:
            best_dist, dist_score = _best_match(dist_hint or text, dist_choices)

        if not best_dist or dist_score < district_threshold:
            status = False
        else:
            district_th = best_dist
            dist_code = dist_name_to_code.get(best_dist, "")
            if not dist_code:
                status = False
    else:
        status = False

    # ---------- 3) Sub-district (within district) ----------
    sub_district_th = ""

    if dist_code and dist_code in sub_districts:
        subs_in_dist = sub_districts.get(dist_code, {})

        sub_choices = []
        for sub_code, sub_obj in subs_in_dist.items():
            if isinstance(sub_obj, dict):
                s_name = (sub_obj.get("name_th") or "").strip()
            else:
                s_name = (str(sub_obj) or "").strip()

            if s_name:
                sub_choices.append(s_name)

        sub_hint = _extract_after_keyword(
            text, keywords=("แขวง", "ตำบล"), stop_words=("เขต", "อำเภอ", "จังหวัด")
        )

        best_sub, sub_score = _find_by_containment(sub_hint or text, sub_choices)
        if not best_sub:
            best_sub, sub_score = _best_match(sub_hint or text, sub_choices)

        if not best_sub or sub_score < subdistrict_threshold:
            status = False
        else:
            sub_district_th = best_sub
    else:
        status = False

    # ---------- 4) address_rest ----------
    # เอาแค่ส่วน "ก่อนคำว่า แขวง/ตำบล/เขต..." 
    address_rest = _cut_before_admin(text, province_th)
    address_rest = re.sub(r"\s+", " ", address_rest).strip()

    return address_rest, sub_district_th, district_th, province_th, status
