import cv2
import numpy as np
import os

def resize_image(image_bgr, width=1280, height=800, keep_ratio=True):
    h, w = image_bgr.shape[:2]

    # ถ้าขนาดตรงแล้ว ไม่ resize ซ้ำ
    if w == width and h == height:
        return image_bgr

    if not keep_ratio:
        return cv2.resize(image_bgr, (width, height))

    # --- keep ratio + pad ---
    scale = min(width / w, height / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(image_bgr, (new_w, new_h))
    canvas = cv2.copyMakeBorder(
        resized,
        (height - new_h) // 2,
        (height - new_h + 1) // 2,
        (width - new_w) // 2,
        (width - new_w + 1) // 2,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )
    return canvas


# def remove_blue_bg_to_white(crop_bgr):
#     """
#     ลบพื้นหลังฟ้า -> ขาว (สำหรับ address)
#     """
#     if crop_bgr is None or crop_bgr.size == 0:
#         return crop_bgr

#     hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)

#     # ช่วงสีฟ้า/น้ำเงินอ่อน (ปรับได้)
#     lower = np.array([80, 15, 120], dtype=np.uint8)
#     upper = np.array([130, 255, 255], dtype=np.uint8)

#     mask = cv2.inRange(hsv, lower, upper)

#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

#     out = crop_bgr.copy()
#     out[mask > 0] = (255, 255, 255)

#     return out


def bg_anycolor_to_white_keep_text(bgr):
    """
    ทำพื้นหลังทุกสี -> ขาว โดยพยายาม 'เก็บตัวอักษร/เส้น' ไว้
    เหมาะกับ OCR (ชื่อ/ที่อยู่/ช่องข้อมูล)
    """
    if bgr is None or bgr.size == 0:
        return bgr

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # ลดนอยส์ก่อน เพื่อให้ threshold เสถียร
    gray_blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # ดึง "ตัวอักษร" ออกมาแบบ adaptive (ทนต่อพื้นหลังหลายสี/ไล่เฉด)
    th = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,  # ปรับได้: 21/31/41
        7    # ปรับได้: 5-15
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)

    # สร้างภาพพื้นหลังขาว แล้วแปะเฉพาะส่วนตัวอักษรกลับเข้าไป
    out = np.full_like(bgr, 255)
    out[th > 0] = bgr[th > 0]

        
    return out
