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

def pad_to_white(crop_bgr, pad_x=30, pad_y=60):
    
    if crop_bgr is None or crop_bgr.size == 0:
        return crop_bgr

    return cv2.copyMakeBorder(
        crop_bgr,
        pad_y, pad_y,     
        pad_x, pad_x,     
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )


def crop_regions(image_bgr, regions, pad_x=20, pad_y=40, save_dir=None ):
    
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    out = {}
    for name, rect in regions.items():

        rect_point = rect[0:4]
        rect_to_bg_white = rect[4]

        c = crop_region(image_bgr, rect_point)
        if c is None or c.size == 0:
            out[name] = None
            continue
        
        if rect_to_bg_white:
            c = bg_anycolor_to_white_keep_text(c) 

        # blurry, score = is_blurry(c)
        # if blurry:
            
        c = enhance_text_clarity(c)

        c = pad_to_white(c, pad_x=pad_x, pad_y=pad_y)
        
        if save_dir:
            save_path = os.path.join(save_dir, f"{name}.jpg")
            cv2.imwrite(save_path, c)
        

        out[name] = c

        
    return out

# def is_blurry(image_bgr, threshold=80.0):
#     """
#     return True ถ้าภาพเบลอ
#     threshold:
#       - 50–70  = เบลอมาก
#       - 70–100 = เบลอนิดหน่อย
#       - >100   = คม
#     """
#     gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
#     fm = cv2.Laplacian(gray, cv2.CV_64F).var()
#     return fm < threshold, fm
