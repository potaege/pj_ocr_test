import cv2

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
