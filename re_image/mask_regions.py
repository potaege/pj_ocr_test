import numpy as np

def mask_image_with_regions(image_bgr, regions, background_color=(255, 255, 255)):
    h, w = image_bgr.shape[:2]

    # พื้นหลังสีขาว
    bg = np.ones((h, w, 3), dtype=np.uint8)
    bg[:] = background_color

    for name, (x, y, rw, rh) in regions.items():
        crop = image_bgr[y:y+rh, x:x+rw]
        if crop.size == 0:
            continue
        bg[y:y+rh, x:x+rw] = crop

    return bg
