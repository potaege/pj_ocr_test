# thai_id_ocr_to_file.py

# ====== MUST BE ON TOP ======
import os
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["GLOG_minloglevel"] = "3"
os.environ["FLAGS_logtostderr"] = "0"
# ===========================

# ติดตั้ง:
#   pip install paddlepaddle paddleocr opencv-python

import cv2
from paddleocr import PaddleOCR

# =======================
# ตั้งค่าตรงนี้
# =======================
IMAGE_PATH = "output_white_background.jpg"        # ใส่ path รูปบัตรของคุณ
OUTPUT_TXT = "ocr_result.txt"     # ไฟล์ output
DEBUG_SAVE_RAW = True             # True = เซฟผลลัพธ์ดิบไว้ดู (ช่วย debug)
RAW_TXT = "ocr_raw.txt"           # ไฟล์เก็บผลลัพธ์ดิบ (ถ้า DEBUG_SAVE_RAW=True)

# =======================
# Helper: ดึงข้อความแบบทน ๆ
# =======================
def collect_texts(obj, out):
    
    if obj is None:
        return

    # กรณีเป็น string ตรง ๆ
    if isinstance(obj, str):
        s = obj.strip()
        if s:
            out.append(s)
        return

    # กรณีเป็น dict
    if isinstance(obj, dict):
        for v in obj.values():
            collect_texts(v, out)
        return

    # กรณีเป็น list/tuple
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

def to_debug_string(obj, max_chars=200000):
    """
    แปลงผลลัพธ์ดิบเป็นข้อความเพื่อ debug (ไม่ต้อง import pprint)
    """
    s = repr(obj)
    if len(s) > max_chars:
        s = s[:max_chars] + "\n...[TRUNCATED]..."
    return s

# =======================
# OCR runner
# =======================

ocr = PaddleOCR(lang="th",use_textline_orientation=True)

def run_ocr(image_bgr):
    """
    พยายามใช้ predict() ก่อน (ตาม warning)
    ถ้าไม่เวิร์ก ค่อย fallback ไป ocr()
    """
    # ocr = PaddleOCR(lang="th", use_angle_cls=True)
    # ocr = PaddleOCR(lang="th",use_textline_orientation=True)

    # 1) ลอง predict
    try:
        res = ocr.predict(image_bgr)
        # บางเวอร์ชันคืน generator → แปลงเป็น list
        if not isinstance(res, (list, tuple, dict, str)) and hasattr(res, "__iter__"):
            res = list(res)
        return res, "predict"
    except Exception:
        pass

    # 2) fallback ocr()
    try:
        res = ocr.ocr(image_bgr)
        if not isinstance(res, (list, tuple, dict, str)) and hasattr(res, "__iter__"):
            res = list(res)
        return res, "ocr"
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"อ่านรูปไม่ได้: {IMAGE_PATH}")

    result, used_api = run_ocr(img)

    # debug: เซฟผลลัพธ์ดิบ
    if DEBUG_SAVE_RAW:
        with open(RAW_TXT, "w", encoding="utf-8") as f:
            f.write(f"USED_API={used_api}\n")
            f.write(to_debug_string(result))

    # เก็บข้อความ
    texts = []
    collect_texts(result, texts)

    # ลบซ้ำ + ลบข้อความสั้น ๆ ที่มักเป็น noise (ปรับได้)
    texts = [t for t in texts if len(t.strip()) >= 2]
    texts = unique_keep_order(texts)

    # เขียนไฟล์
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(texts))

    print(f"✅ Done. API={used_api} | lines={len(texts)} | saved={OUTPUT_TXT}")
    if DEBUG_SAVE_RAW:
        print(f"🧾 Raw saved={RAW_TXT} (เอาไว้เช็กว่า OCR คืนค่าอะไร)")

if __name__ == "__main__":
    main()
