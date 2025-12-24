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
ocr = PaddleOCR(lang="th", use_textline_orientation=True)

# =======================
# พิกัด crop (x, y, w, h)  <<== ของคุณ
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
    preprocess แบบ soft:
    - ขยายภาพช่วยตัวอักษรเล็ก
    - ใส่ขอบกันตัดชิด
    - sharpen เบา ๆ
    (ไม่ threshold โหด เพราะไทยแตกง่าย)
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
    """
    ดึง string ที่น่าจะเป็นข้อความ OCR จากโครงสร้างผลลัพธ์ทุกแบบ (ทนสุด)
    """
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
    # ตัดหัวกวนใจที่เด้งมาบ่อย
    s = re.sub(r"^(min general|general|min)\s+", "", s, flags=re.IGNORECASE)
    return s.strip()

def postprocess_field(key: str, text: str) -> str:   ## คิดว่าน่าจะเป็นที่ตรงนี้ที่ไม่มี แต่แก้ citizen_id ด้วย
    t = normalize_text(text)
    print(t)

    if key == "citizen_id":
        digits = re.findall(r"\d", t)
        if len(digits) >= 13:
            return "".join(digits[:13])
        return t

    elif key in ["birthday", "issue_date", "expiry_date"]:
        return t.replace("c ", "").strip()

    return t

def ocr_text_from_crop(key: str, crop_bgr, debug_raw_path=None):
    
    crop_pp = preprocess_crop_soft(crop_bgr)

    # OCR
    try:
        res = ocr.ocr(crop_pp, det=True, rec=True, cls=False)
    except Exception:
        # fallback เผื่อบางเวอร์ชัน
        res = ocr.ocr(crop_pp)

    # debug raw
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
            crop_pp = preprocess_crop_soft(crop)
            cv2.imwrite(os.path.join(CROP_DIR, f"{key}_pp.png"), crop_pp)

    # เขียนผลลงไฟล์
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for k, v in results.items():
            f.write(f"{k}: {v}\n")

    print("✅ Done. saved:", OUTPUT_TXT)
    if DEBUG_SAVE_CROPS:
        print("🖼️ Crops saved in:", CROP_DIR)
        print("🧾 OCR raw per field saved as *_ocr_raw.txt in crops/")

if __name__ == "__main__":
    main()
