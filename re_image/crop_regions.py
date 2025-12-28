# re_image/crop_regions.py
import cv2
import os
import numpy as np
from re_image.preprocess import bg_anycolor_to_white_keep_text

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

        c = pad_to_white(c, pad_x=pad_x, pad_y=pad_y)
        out[name] = c

        
    return out
