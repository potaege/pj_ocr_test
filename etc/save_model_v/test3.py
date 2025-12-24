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

def crop_image(img, rect, pad=(0, 0, 0, 0)):
    x, y, w, h = rect
    pt, pb, pl, pr = pad
    H, W = img.shape[:2]
    x1 = max(0, x - pl)
    y1 = max(0, y - pt)
    x2 = min(W, x + w + pr)
    y2 = min(H, y + h + pb)
    if x2 <= x1 or y2 <= y1:
        return None
    return img[y1:y2, x1:x2]

def normalize_text(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"^(min general|general|min)\s+", "", s, flags=re.IGNORECASE)
    return s.strip()

# =======================
# preprocess (นิ่ง ๆ)
# =======================
def add_border(img, pad=24):
    return cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))

def preprocess_soft(crop_bgr, scale=2.6, pad=26):
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr
    h, w = crop_bgr.shape[:2]
    crop = cv2.resize(crop_bgr, (max(1, int(w*scale)), max(1, int(h*scale))), interpolation=cv2.INTER_CUBIC)
    crop = add_border(crop, pad)
    blur = cv2.GaussianBlur(crop, (0, 0), 1.0)
    sharp = cv2.addWeighted(crop, 1.5, blur, -0.5, 0)
    return sharp

def preprocess_digits(crop_bgr, scale=3.2, pad=34):
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr
    h, w = crop_bgr.shape[:2]
    crop = cv2.resize(crop_bgr, (max(1, int(w*scale)), max(1, int(h*scale))), interpolation=cv2.INTER_CUBIC)
    crop = add_border(crop, pad)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

# =======================
# OCR calls
# =======================
def ocr_call(img_bgr, det: bool):
    try:
        return ocr.ocr(img_bgr, det=det, rec=True, cls=True)
    except Exception:
        # fallback เผื่อบางเวอร์ชัน
        return ocr.ocr(img_bgr)

# =======================
# Robust parsers (กันหายหมด)
# =======================
def unique_keep_order(lst):
    out, seen = [], set()
    for x in lst:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def collect_all_strings(obj, out):
    """fallback: กวาด string ทุกตัวจากโครงสร้างใด ๆ"""
    if obj is None:
        return
    if isinstance(obj, str):
        s = obj.strip()
        if s:
            out.append(s)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            collect_all_strings(v, out)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            collect_all_strings(v, out)
        return

def parse_det_items(res):
    """
    พยายามดึง (cy,cx,text) จากผล det=True ทุกรูปแบบ
    รูปแบบปกติ: res = [ [ [box, (text,score)], ... ] ] (หลายหน้าได้)
    """
    items = []
    if not isinstance(res, list):
        return items

    # flatten pages
    pages = res
    for page in pages:
        if not isinstance(page, list):
            continue
        for line in page:
            if not isinstance(line, (list, tuple)) or len(line) < 2:
                continue
            box = line[0]
            pack = line[1]
            text = None
            if isinstance(pack, (list, tuple)) and len(pack) >= 1 and isinstance(pack[0], str):
                text = pack[0]
            if not text or not text.strip():
                continue

            try:
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                cx = float(sum(xs)) / len(xs)
                cy = float(sum(ys)) / len(ys)
            except Exception:
                cx, cy = 0.0, 0.0

            items.append((cy, cx, text.strip()))

    items.sort(key=lambda t: (t[0], t[1]))
    return items

def parse_text_any(res):
    """
    ใช้ได้ทั้ง det=False และ fallback:
    - ถ้า det=False: มักเป็น list ของ [text, score] หรือ [(text,score)] ในหลายชั้น
    - ถ้าไม่เข้ารูปแบบ: กวาด string ทั้งหมด
    """
    texts = []

    # เคส det=False ที่พบบ่อย: [[('text', score)], ...] หรือ [('text',score), ...] หรือ [['text',score],...]
    def walk(obj):
        if obj is None:
            return
        if isinstance(obj, str):
            s = obj.strip()
            if s:
                texts.append(s)
            return
        if isinstance(obj, (list, tuple)):
            # ถ้าเป็น (text, score)
            if len(obj) == 2 and isinstance(obj[0], str) and isinstance(obj[1], (int, float)):
                if obj[0].strip():
                    texts.append(obj[0].strip())
                return
            # ถ้าเป็น [text, score]
            if len(obj) == 2 and isinstance(obj[0], str):
                if obj[0].strip():
                    texts.append(obj[0].strip())
                return
            for v in obj:
                walk(v)
            return
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
            return

    walk(res)

    if not texts:
        collect_all_strings(res, texts)

    texts = unique_keep_order([t for t in texts if t.strip()])
    return " ".join(texts).strip()

# =======================
# Thai ID checksum
# =======================
def thai_id_is_valid(id13: str) -> bool:
    if not re.fullmatch(r"\d{13}", id13 or ""):
        return False
    nums = [int(c) for c in id13]
    s = 0
    for i in range(12):
        s += nums[i] * (12 - i)
    check = (11 - (s % 11)) % 10
    return check == nums[12]

def pick_thai_id_from_digits(digits_all: str) -> str:
    if len(digits_all) < 13:
        return digits_all
    for i in range(0, len(digits_all) - 13 + 1):
        cand = digits_all[i:i+13]
        if thai_id_is_valid(cand):
            return cand
    return digits_all[:13]

# =======================
# Postprocess per field
# =======================
THAI_WORD_RE = re.compile(r"[ก-๙]+")
TITLE_LIST = ["นาย", "นาง", "นางสาว"]

def post_name_th(text: str) -> str:
    t = normalize_text(text)
    words = THAI_WORD_RE.findall(t)
    # ตัดคำขยะสั้น ๆ
    words = [w for w in words if len(w) >= 2]

    # หา title แล้วเอา 2 คำถัดไป
    for i, w in enumerate(words):
        if w in TITLE_LIST:
            nxt = words[i+1:i+3]
            if len(nxt) >= 2:
                return f"{w} {nxt[0]} {nxt[1]}"
            if len(nxt) == 1:
                return f"{w} {nxt[0]}"
            return w

    # fallback: เลือก 2 คำที่ยาวสุด (กันนามสกุล/ชื่อสลับมั่ว)
    if len(words) >= 2:
        ws = sorted(words, key=len, reverse=True)
        a, b = ws[0], ws[1]
        # ปกติจะอยากได้ "ชื่อ นามสกุล" แต่แยกยาก -> คืน 2 คำหลักก่อน
        return f"{a} {b}"
    return " ".join(words).strip()

def post_religion(text: str) -> str:
    t = normalize_text(text)
    words = THAI_WORD_RE.findall(t)
    words = [w for w in words if len(w) >= 2]
    joined = " ".join(words).replace("พทธ", "พุทธ").strip()
    # ศาสนาส่วนใหญ่คำเดียว
    return joined.split()[0] if joined else ""

def post_address(text: str) -> str:
    t = normalize_text(text)
    # เก็บไทย+เลข+สัญลักษณ์พื้นฐาน
    t = re.sub(r"[^ก-๙0-9\s\.\,\/\-\(\)]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    toks = t.split()
    keep = []
    for tok in toks:
        if re.fullmatch(r"25\d{2}", tok):  # ตัดปี 25xx ที่ชอบหลอน
            continue
        if re.fullmatch(r"\d{1,6}", tok):
            keep.append(tok)
            continue
        if re.search(r"[ก-๙]", tok) and len(tok) >= 2:
            keep.append(tok)
            continue
        if tok in ["ถ.", "ซ.", "ต.", "อ.", "จ.", "แขวง", "เขต", "จังหวัด", "กรุงเทพมหานคร", "กทม."]:
            keep.append(tok)

    return " ".join(keep).strip()

def post_date(text: str) -> str:
    t = normalize_text(text).replace("c ", " ").strip()
    t = re.sub(r"\s+", " ", t).strip()

    # กันสลับ "มี.ค. 2571 21" -> "21 มี.ค. 2571"
    m = re.search(r"(\d{1,2})\s*(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s*(25\d{2})", t)
    if m:
        return f"{m.group(1)} {m.group(2)} {m.group(3)}"
    m2 = re.search(r"(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s*(25\d{2})\s*(\d{1,2})", t)
    if m2:
        return f"{m2.group(3)} {m2.group(1)} {m2.group(2)}"
    return t

# =======================
# Field OCR
# =======================
def ocr_field(key: str, crop_bgr, debug_txt_path=None) -> str:
    if crop_bgr is None or crop_bgr.size == 0:
        return ""

    # เลือก preprocess
    if key == "citizen_id":
        img_pp = preprocess_digits(crop_bgr)
    else:
        img_pp = preprocess_soft(crop_bgr, scale=2.7, pad=28)

    # ฟิลด์ที่ต้องเรียง order: ใช้ det=True ก่อน
    need_order = key in ["citizen_id", "name_lastname_th", "religion", "address"]
    use_det_first = need_order

    chosen_raw_text = ""

    if use_det_first:
        res_det = ocr_call(img_pp, det=True)
        items = parse_det_items(res_det)
        if items:
            chosen_raw_text = " ".join([it[2] for it in items])
        else:
            # fallback det=False ถ้า det=True ไม่ได้อะไร (กันหายหมด)
            res_nd = ocr_call(img_pp, det=False)
            chosen_raw_text = parse_text_any(res_nd)

        if debug_txt_path:
            with open(debug_txt_path, "w", encoding="utf-8") as f:
                f.write(f"key={key} (det-first)\n")
                f.write(f"det_items_count={len(items)}\n")
                for cy, cx, tx in items[:50]:
                    f.write(f"({cy:.1f},{cx:.1f}) {tx}\n")
                f.write(f"\nraw_text={repr(chosen_raw_text)}\n")

    else:
        res_nd = ocr_call(img_pp, det=False)
        chosen_raw_text = parse_text_any(res_nd)
        if debug_txt_path:
            with open(debug_txt_path, "w", encoding="utf-8") as f:
                f.write(f"key={key} (nodet)\n")
                f.write(f"raw_text={repr(chosen_raw_text)}\n")

    # postprocess ตาม field
    t = normalize_text(chosen_raw_text)

    if key == "citizen_id":
        digits_all = "".join(re.findall(r"\d", t))
        return pick_thai_id_from_digits(digits_all)

    if key == "name_lastname_th":
        return post_name_th(t)

    if key == "religion":
        return post_religion(t)

    if key == "address":
        return post_address(t)

    if key in ["birthday", "issue_date", "expiry_date"]:
        return post_date(t)

    return t

# =======================
# main
# =======================
def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"อ่านรูปไม่ได้: {IMAGE_PATH}")

    if DEBUG_SAVE_CROPS:
        ensure_dir(CROP_DIR)

    PAD_BY_KEY = {
        "citizen_id": (18, 18, 130, 80),
        "name_lastname_th": (16, 16, 70, 70),
        "name_eng": (12, 12, 30, 30),
        "lastname_eng": (12, 12, 30, 30),
        "birthday": (12, 12, 30, 30),
        "religion": (16, 16, 70, 70),
        "address": (22, 22, 80, 80),
        "issue_date": (12, 12, 35, 35),
        "expiry_date": (12, 12, 35, 35),
    }

    results = {}

    for key, rect in REGIONS.items():
        crop = crop_image(img, rect, pad=PAD_BY_KEY.get(key, (0,0,0,0)))

        if DEBUG_SAVE_CROPS and crop is not None:
            cv2.imwrite(os.path.join(CROP_DIR, f"{key}_raw.png"), crop)

        debug_txt = os.path.join(CROP_DIR, f"{key}_ocr_debug.txt")
        results[key] = ocr_field(key, crop, debug_txt_path=debug_txt)

        if DEBUG_SAVE_CROPS and crop is not None:
            cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp_soft.png"), preprocess_soft(crop))
            if key == "citizen_id":
                cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp_digits.png"), preprocess_digits(crop))

    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for k, v in results.items():
            f.write(f"{k}: {v}\n")

    print("✅ Done. saved:", OUTPUT_TXT)
    if DEBUG_SAVE_CROPS:
        print("🖼️ Crops saved in:", CROP_DIR)
        print("🧾 Debug logs saved as *_ocr_debug.txt in crops/")

if __name__ == "__main__":
    main()
