# re_image/crop_regions.py
import cv2
import os
import numpy as np
from re_image.preprocess import bg_anycolor_to_white_keep_text

def enhance_text_clarity(image_bgr):
    """
    เน้นความคมชัดของขอบ (Sharpen) โดยไม่ทำลายรายละเอียด
    เหมาะสำหรับ OCR ที่ต้องการเห็นขอบตัวอักษรชัดๆ
    """
    if image_bgr is None or image_bgr.size == 0:
        return image_bgr

    # 1. แปลงเป็น Grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 2. ลบ Noise ออกเล็กน้อยก่อน
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)

    # 3. ทำ Unsharp Masking
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)

    # 4. ปรับ Contrast ให้เข้มขึ้นอีก (ไม่ต้องใช้ Threshold)
    # ใช้ Normalization ดึงช่วงสีให้เต็มกราฟ (ดำสุดเป็น 0, ขาวสุดเป็น 255)
    final_img = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)

    final_bgr = cv2.cvtColor(final_img, cv2.COLOR_GRAY2BGR)

    return final_bgr

def crop_region(image_bgr, rect):
    x, y, w, h = rect
    H, W = image_bgr.shape[:2]
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(W, x + w)
    y2 = min(H, y + h)
    crop = image_bgr[y1:y2, x1:x2]
    return crop

def pad_to_white(crop_bgr, pad_x=20, pad_y=40):
    """
    pad_x = ซ้าย-ขวา
    pad_y = บน-ล่าง (ให้มากกว่าสำหรับภาษาไทย)
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr

    return cv2.copyMakeBorder(
        crop_bgr,
        pad_y, pad_y,     # top, bottom  👈 เพิ่มด้านสูง
        pad_x, pad_x,     # left, right
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )


def crop_regions(image_bgr, regions, pad_x=20, pad_y=40, save_dir=None):
    """
    คืน dict: {field_name: crop_img_bgr}
    ถ้า save_dir != None จะเขียนไฟล์ crop_<field>.jpg ลงโฟลเดอร์นั้น
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    out = {}
    for name, rect in regions.items():

        rect_point = rect[0:4]
        rect_to_bg_white = rect[4]

        c = crop_region(image_bgr, rect[0:4])
        if c is None or c.size == 0:
            out[name] = None
            continue
        
        if rect_to_bg_white:
            c = bg_anycolor_to_white_keep_text(c) 

        c = enhance_text_clarity(c)

        c = pad_to_white(c, pad_x=pad_x, pad_y=pad_y)

        if save_dir is not None:
            save_path = os.path.join(save_dir, f"{name}.jpg")
            cv2.imwrite(save_path, c) # ใช้ imwrite บันทึกไฟล์

        out[name] = c

        
    return out
