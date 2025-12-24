import os
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["GLOG_minloglevel"] = "3"
os.environ["FLAGS_logtostderr"] = "0"

from paddleocr import PaddleOCR

# โหลดโมเดลครั้งเดียว
ocr = PaddleOCR(lang="th", use_textline_orientation=True)

def run_ocr(image_bgr):
    # 1) ใช้ predict ก่อน
    try:
        res = ocr.predict(image_bgr)
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
