# thai_id_crop_ocr_to_file.py

import os
os.environ["GLOG_minloglevel"] = "3"
os.environ["FLAGS_logtostderr"] = "0"

import re
import cv2
import numpy as np
from paddleocr import PaddleOCR

# =======================
# ตั้งค่า
# =======================
IMAGE_PATH = "thai_id.jpg"
OUTPUT_TXT = "ocr_fields.txt"

DEBUG_SAVE_CROPS = True
CROP_DIR = "crops"

# ✅ init OCR ครั้งเดียว
ocr = PaddleOCR(lang="th", use_angle_cls=True)

# =======================
# พิกัด crop (x, y, w, h)  <<== ของคุณ (ห้ามแก้)
# =======================
REGIONS = {
    "citizen_id": (554, 82, 421, 54),
    "name_lastname_th": (355, 148, 885, 99),
    "name_eng": (495, 240, 554, 54),
    "lastname_eng": (561, 293, 519, 47),
    "birthday": (550, 340, 279, 66),
    "religion": (529, 470, 122, 47),
    "address": (135, 511, 763, 121),
    "issue_date": (137, 632, 190, 38),
    "expiry_date": (700, 623, 192, 45),
}

# =======================
# utils
# =======================
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def crop_image(img, rect):
    x, y, w, h = rect
    H, W = img.shape[:2]
    x = max(0, x); y = max(0, y)
    w = max(1, w); h = max(1, h)
    x2 = min(W, x + w)
    y2 = min(H, y + h)
    return img[y:y2, x:x2]

def preprocess_crop_soft(crop_bgr, scale=2.2, pad=22):
    """
    ✅ ใช้ตัวเดิมเป็น default ทุกฟิลด์ (กันผลข้างเคียง)
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr

    h, w = crop_bgr.shape[:2]
    crop = cv2.resize(
        crop_bgr,
        (max(1, int(w * scale)), max(1, int(h * scale))),
        interpolation=cv2.INTER_CUBIC
    )

    crop = cv2.copyMakeBorder(
        crop, pad, pad, pad, pad,
        borderType=cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )

    blur = cv2.GaussianBlur(crop, (0, 0), 1.0)
    sharp = cv2.addWeighted(crop, 1.6, blur, -0.6, 0)
    return sharp

def collect_texts(obj, out):
    """ดึง string จากโครงสร้างผลลัพธ์ทุกแบบ (ทนสุด)"""
    if obj is None:
        return
    if isinstance(obj, str):
        s = obj.strip()
        if s:
            out.append(s)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            collect_texts(v, out)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            collect_texts(v, out)
        return

def unique_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def normalize_text(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"^(min general|general|min)\s+", "", s, flags=re.IGNORECASE)
    return s.strip()

def ocr_call(img_bgr):
    try:
        return ocr.ocr(img_bgr, det=True, rec=True, cls=False)
    except Exception:
        return ocr.ocr(img_bgr)

# =======================
# ✅ preprocess เพิ่ม เฉพาะ 3 ฟิลด์ (ไม่กระทบช่องอื่น)
# =======================
def preprocess_clahe(crop_bgr, scale=3.0, pad=28):
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr
    h, w = crop_bgr.shape[:2]
    crop = cv2.resize(crop_bgr, (max(1, int(w*scale)), max(1, int(h*scale))), interpolation=cv2.INTER_CUBIC)
    crop = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255,255,255))
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    g = clahe.apply(gray)
    g = cv2.GaussianBlur(g, (3,3), 0)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

def preprocess_adapt(crop_bgr, scale=3.0, pad=30):
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr
    h, w = crop_bgr.shape[:2]
    crop = cv2.resize(crop_bgr, (max(1, int(w*scale)), max(1, int(h*scale))), interpolation=cv2.INTER_CUBIC)
    crop = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255,255,255))
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 40, 40)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 9)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

# =======================
# ✅ FIX เฉพาะ 3 ฟิลด์
# =======================
THAI_WORD_RE = re.compile(r"[ก-๙]+")
TITLE_LIST = ["นาย", "นาง", "นางสาว"]
RELIGION_WHITELIST = ["พุทธ", "อิสลาม", "คริสต์", "ฮินดู", "ซิกข์", "ไม่นับถือศาสนา"]

def fix_name_lastname_th(text: str) -> str:
    t = normalize_text(text)
    words = THAI_WORD_RE.findall(t)

    bad = {"กบล", "กล", "บล", "กบ", "นายกบล"}
    words = [w for w in words if len(w) >= 2 and w not in bad]

    # title + ชื่อ + สกุล (ต้องพยายามให้ครบ 3 ชิ้น)
    for i, w in enumerate(words):
        if w in TITLE_LIST:
            nxt = words[i+1:i+4]  # เผื่อ OCR แทรกคำหลอก
            # เอา 2 คำถัดไปที่ “ยาวสุด” เป็นชื่อ/สกุล
            cand = [x for x in nxt if len(x) >= 2]
            if len(cand) >= 2:
                cand2 = sorted(cand, key=len, reverse=True)[:2]
                # รักษาลำดับเดิม: เลือกตามการปรากฏจริง
                ordered = []
                for x in nxt:
                    if x in cand2 and x not in ordered:
                        ordered.append(x)
                if len(ordered) >= 2:
                    return f"{w} {ordered[0]} {ordered[1]}"
            if len(cand) == 1:
                return f"{w} {cand[0]}"
            return w

    # fallback: เอา 2 คำที่ยาวสุด
    if len(words) >= 2:
        ws = sorted(words, key=len, reverse=True)
        return f"{ws[0]} {ws[1]}"
    return " ".join(words).strip()

def fix_religion(text: str) -> str:
    t = normalize_text(text)
    thai = " ".join(THAI_WORD_RE.findall(t))
    thai = thai.replace("พทธ", "พุทธ").replace("พท", "พุทธ")
    thai = thai.replace("อสิลาม", "อิสลาม").replace("อลาม", "อิสลาม")
    thai = thai.replace("ครสต", "คริสต์").replace("ครส", "คริสต์")
    thai = thai.replace("ฮนด", "ฮินดู")
    thai = thai.replace("ซกข", "ซิกข์").replace("สกข", "ซิกข์")
    for w in RELIGION_WHITELIST:
        if w in thai:
            return w
    return ""

def fix_address(text: str) -> str:
    t = normalize_text(text)
    t = re.sub(r"[^ก-๙0-9\s\.\,\/\-\(\)]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    toks = t.split()
    keep = []
    for tok in toks:
        if re.fullmatch(r"25\d{2}", tok):
            continue
        if re.fullmatch(r"\d{1,6}", tok):
            keep.append(tok); continue
        if re.search(r"[ก-๙]", tok) and len(tok) >= 2:
            keep.append(tok); continue
        if tok in ["ถ.", "ซ.", "ต.", "อ.", "จ.", "แขวง", "เขต", "จังหวัด", "กรุงเทพมหานคร", "กทม."]:
            keep.append(tok)

    return " ".join(keep).strip()

def score_candidate(key: str, raw: str) -> int:
    t = normalize_text(raw)
    thai_cnt = len(re.findall(r"[ก-๙]", t))
    digit_cnt = len(re.findall(r"\d", t))

    if key == "name_lastname_th":
        sc = thai_cnt * 10
        if any(tt in t for tt in TITLE_LIST): sc += 250
        words = [w for w in THAI_WORD_RE.findall(t) if len(w) >= 2]
        if len(words) >= 3: sc += 250  # อยากได้ นาย + ชื่อ + สกุล
        if "กบล" in t: sc -= 400
        return sc

    if key == "religion":
        sc = thai_cnt * 10
        if fix_religion(t): sc += 800
        if "เสนา" in t: sc -= 400
        return sc

    if key == "address":
        sc = thai_cnt * 8 + digit_cnt * 4
        if re.search(r"\b\d{1,4}\b", t): sc += 150   # มีเลขบ้าน เช่น 130
        if any(k in t for k in ["ถ.", "แขวง", "เขต", "จังหวัด", "กรุงเทพมหานคร", "กทม."]): sc += 250
        return sc

    return thai_cnt + digit_cnt

# =======================
# postprocess_field (แตะ 3 field เท่านั้น)
# =======================
def postprocess_field(key: str, text: str) -> str:
    t = normalize_text(text)

    if key == "citizen_id":
        digits = re.findall(r"\d", t)
        if len(digits) >= 13:
            return "".join(digits[:13])
        return "".join(digits)

    if key in ["birthday", "issue_date", "expiry_date"]:
        return t.replace("c ", "").strip()

    # ✅ แก้เฉพาะ 3 ฟิลด์
    if key == "name_lastname_th":
        return fix_name_lastname_th(t)

    if key == "religion":
        return fix_religion(t)

    if key == "address":
        return fix_address(t)

    return t

# =======================
# OCR per crop
# =======================
def ocr_text_from_crop(key: str, crop_bgr, debug_raw_path=None):
    if crop_bgr is None or crop_bgr.size == 0:
        return ""

    # ✅ multi-pass เฉพาะ 3 ช่อง (ไม่แตะช่องอื่น)
    if key in ["name_lastname_th", "religion", "address"]:
        variants = [
            ("soft_default", preprocess_crop_soft(crop_bgr, scale=2.2, pad=22)),  # ตัวเดิม
            ("soft_big", preprocess_crop_soft(crop_bgr, scale=2.8, pad=28)),
            ("clahe", preprocess_clahe(crop_bgr, scale=3.2, pad=30)),
            ("adapt", preprocess_adapt(crop_bgr, scale=3.0, pad=30)),
        ]

        best_raw, best_sc = "", -10**9
        logs = []
        for tag, img_pp in variants:
            res = ocr_call(img_pp)
            texts = []
            collect_texts(res, texts)
            texts = unique_keep_order([x for x in texts if x.strip()])
            joined = " ".join(texts).strip()
            sc = score_candidate(key, joined)
            logs.append((tag, sc, joined))
            if sc > best_sc:
                best_sc, best_raw = sc, joined

        if debug_raw_path:
            with open(debug_raw_path, "w", encoding="utf-8") as f:
                for tag, sc, joined in logs:
                    f.write(f"[{tag}] score={sc} text={repr(joined)}\n")
                f.write(f"\nCHOSEN score={best_sc} text={repr(best_raw)}\n")

        return postprocess_field(key, best_raw)

    # ✅ ช่องอื่นทั้งหมด: ใช้ของเดิมเหมือนก่อน (กันเพี้ยน)
    crop_pp = preprocess_crop_soft(crop_bgr, scale=2.2, pad=22)
    res = ocr_call(crop_pp)

    if debug_raw_path:
        with open(debug_raw_path, "w", encoding="utf-8") as f:
            f.write(repr(res))

    texts = []
    collect_texts(res, texts)
    texts = [t for t in texts if len(t.strip()) >= 1]
    texts = unique_keep_order(texts)

    joined = " ".join(texts).strip()
    return postprocess_field(key, joined)

def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"อ่านรูปไม่ได้: {IMAGE_PATH}")

    if DEBUG_SAVE_CROPS:
        ensure_dir(CROP_DIR)

    results = {}

    for key, rect in REGIONS.items():
        crop = crop_image(img, rect)

        if DEBUG_SAVE_CROPS:
            cv2.imwrite(os.path.join(CROP_DIR, f"{key}_raw.png"), crop)

        debug_raw_txt = os.path.join(CROP_DIR, f"{key}_ocr_raw.txt")
        text = ocr_text_from_crop(key, crop, debug_raw_path=debug_raw_txt)
        results[key] = text

        if DEBUG_SAVE_CROPS:
            cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp.png"), preprocess_crop_soft(crop, scale=2.2, pad=22))
            if key in ["name_lastname_th", "religion", "address"]:
                cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp_soft_big.png"), preprocess_crop_soft(crop, scale=2.8, pad=28))
                cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp_clahe.png"), preprocess_clahe(crop, scale=3.2, pad=30))
                cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp_adapt.png"), preprocess_adapt(crop, scale=3.0, pad=30))

    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for k, v in results.items():
            f.write(f"{k}: {v}\n")

    print("✅ Done. saved:", OUTPUT_TXT)
    if DEBUG_SAVE_CROPS:
        print("🖼️ Crops saved in:", CROP_DIR)
        print("🧾 OCR debug per field saved as *_ocr_raw.txt in crops/")

if __name__ == "__main__":
    main()
