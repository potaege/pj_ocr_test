from rapidfuzz import process, fuzz
import re

ADDRESS_WORD = "ที่อยู่"

# ----------------------------
# 1) basic helpers
# ----------------------------
def _best_match(text: str, choices: list[str]):
    """Return (best_choice, score)."""
    if not choices:
        return None, 0
    res = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    if not res:
        return None, 0
    best, score, _ = res
    return best, score


def _normalize_address(text: str) -> str:
    """
    Normalize OCR text:
    - unify dash variants
    - keep Thai chars, digits, and address punct (/ - . ( ))
    - add spaces around punct to reduce glue
    - collapse spaces
    """
    if not isinstance(text, str):
        return ""

    # normalize dash variants to '-'
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")

    # keep only useful chars
    text = re.sub(r"[^0-9ก-๙\s\/\-\.\(\)]", " ", text)

    # put spaces around punct to avoid sticking to words
    text = re.sub(r"([\/\-\.\(\)])", r" \1 ", text)

    # collapse spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_thai_digit_glue(text: str) -> str:
    """
    Split Thai<->digit glue:
      ก123 -> ก 123
      123ก -> 123 ก
    """
    if not text:
        return ""
    text = re.sub(r"([ก-๙])([0-9])", r"\1 \2", text)
    text = re.sub(r"([0-9])([ก-๙])", r"\1 \2", text)
    return text


def strip_address_word_fuzzy(text: str, threshold: int = 80) -> str:
    """
    If the head of text fuzzy-matches "ที่อยู่" >= threshold, remove the first token.
    (No "after must be digit" check, as requested.)
    """
    if not isinstance(text, str):
        return ""

    t = text.strip()
    if not t:
        return t

    head = t[:25]  # check only the beginning
    score = fuzz.partial_ratio(head, ADDRESS_WORD)
    if score < threshold:
        return t

    # remove first token (handles: ที่อยู130 / ที่อยู่ 130 / ที่อู่99/1)
    t = re.sub(r"^\s*\S+\s*", "", t, count=1)
    return t.strip()


def _clean_token(tok: str) -> str:
    """
    Clean token for building address_rest:
    - drop pure punct tokens
    - strip punct at ends, keep middle (e.g., 12/3-4 stays)
    """
    if not tok:
        return ""
    if re.fullmatch(r"[\/\-\.\(\)]+", tok):
        return ""
    tok = tok.strip(" .-()/")
    return tok.strip()


def _tokens(text: str) -> list[str]:
    return [t for t in text.split(" ") if t.strip()]


# ----------------------------
# 2) main parser (tail-first)
# ----------------------------
def parse_admin_from_address(
    address_text: str,
    provinces: dict,
    districts: dict,
    sub_districts: dict,
    address_word_threshold: int = 80,
    province_threshold: int = 30,
    district_threshold: int = 30,
    subdistrict_threshold: int = 30,
):
    
    if not isinstance(address_text, str) or not address_text.strip():
        return "", "", "", "", False

    # A) preprocess
    text = _normalize_address(address_text)
    text = _split_thai_digit_glue(text)
    text = strip_address_word_fuzzy(text, threshold=address_word_threshold)

    # re-normalize after stripping
    text = _normalize_address(text)
    if not text:
        return "", "", "", "", False

    toks = _tokens(text)

    # B) build province choices
    prov_choices: list[str] = []
    prov_name_to_code: dict[str, str] = {}
    for prov_code, obj in provinces.items():
        name_th = (obj.get("name_th") or "").strip()
        if name_th:
            prov_choices.append(name_th)
            prov_name_to_code[name_th] = prov_code

    status = True

    # C) find province from tail (try growing tail spans)
    province_th = ""
    prov_code = ""

    best_prov = None
    best_score = -1
    best_start = None  # start index of tail span used (conservative cut)

    for start in range(len(toks) - 1, -1, -1):
        cand = " ".join(toks[start:])
        cand = _normalize_address(cand)
        if not cand:
            continue
        b, s = _best_match(cand, prov_choices)
        if b and s > best_score:
            best_prov, best_score = b, s
            best_start = start
        if best_score >= 95:
            break

    if not best_prov or best_score < province_threshold:
        status = False
        remaining = toks[:]  # still keep going, but will likely fail district/subdistrict
    else:
        province_th = best_prov
        prov_code = prov_name_to_code.get(best_prov, "")
        remaining = toks[:best_start] if best_start is not None else toks[:]

    # D) district within province (tail-first on remaining)
    district_th = ""
    dist_code = ""

    if prov_code and prov_code in districts:
        prov_districts = districts.get(prov_code, {})
        dist_choices: list[str] = []
        dist_name_to_code: dict[str, str] = {}

        for d_code, d_obj in prov_districts.items():
            d_name = (d_obj.get("name_th") if isinstance(d_obj, dict) else str(d_obj) or "").strip()
            if d_name:
                dist_choices.append(d_name)
                dist_name_to_code[d_name] = d_code

        best_dist = None
        best_dist_score = -1
        best_dist_start = None

        for start in range(len(remaining) - 1, -1, -1):
            cand = " ".join(remaining[start:])
            cand = _normalize_address(cand)
            if not cand:
                continue
            b, s = _best_match(cand, dist_choices)
            if b and s > best_dist_score:
                best_dist, best_dist_score = b, s
                best_dist_start = start
            if best_dist_score >= 95:
                break

        if not best_dist or best_dist_score < district_threshold:
            status = False
        else:
            district_th = best_dist
            dist_code = dist_name_to_code.get(best_dist, "")
            if not dist_code:
                status = False

        if best_dist_start is not None:
            remaining = remaining[:best_dist_start]
    else:
        status = False

    # E) subdistrict within district (tail-first on remaining)
    sub_district_th = ""

    if dist_code and dist_code in sub_districts:
        subs_in_dist = sub_districts.get(dist_code, {})
        sub_choices: list[str] = []

        for sub_code, sub_obj in subs_in_dist.items():
            s_name = (sub_obj.get("name_th") if isinstance(sub_obj, dict) else str(sub_obj) or "").strip()
            if s_name:
                sub_choices.append(s_name)

        best_sub = None
        best_sub_score = -1
        best_sub_start = None

        for start in range(len(remaining) - 1, -1, -1):
            cand = " ".join(remaining[start:])
            cand = _normalize_address(cand)
            if not cand:
                continue
            b, s = _best_match(cand, sub_choices)
            if b and s > best_sub_score:
                best_sub, best_sub_score = b, s
                best_sub_start = start
            if best_sub_score >= 95:
                break

        if not best_sub or best_sub_score < subdistrict_threshold:
            status = False
        else:
            sub_district_th = best_sub

        if best_sub_start is not None:
            remaining = remaining[:best_sub_start]
    else:
        status = False

    # F) remaining => address_rest
    cleaned = []
    for t in remaining:
        ct = _clean_token(t)
        if ct:
            cleaned.append(ct)
    address_rest = " ".join(cleaned).strip()

    return address_rest, sub_district_th, district_th, province_th, status


# ----------------------------
# 3) quick test (optional)
# ----------------------------
if __name__ == "__main__":
    # Example: you must provide real dictionaries in your project
    provinces = {"10": {"name_th": "กรุงเทพมหานคร"}}
    districts = {"10": {"1009": {"name_th": "คันนายาว"}}}
    sub_districts = {"1009": {"100901": {"name_th": "รามอินทรา"}}}

    s = "ที่อยู130 ถ.คู้บอน แขวงรามอินทรา เขตคันนายาว กรงเทพมหานคร - −"
    print(parse_admin_from_address(s, provinces, districts, sub_districts))
