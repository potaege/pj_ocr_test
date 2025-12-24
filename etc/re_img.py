import cv2
import numpy as np

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

# โหลดภาพ
img = cv2.imread("thai_id.jpg")
h, w = img.shape[:2]

# สร้างภาพสีขาวทั้งภาพ
white_img = np.ones((h, w, 3), dtype=np.uint8) * 255

# คืนค่าเฉพาะบริเวณที่อยู่ใน REGIONS
for (x, y, rw, rh) in REGIONS.values():
    crop = img[y:y+rh, x:x+rw]
    white_img[y:y+rh, x:x+rw] = crop

# บันทึกผลลัพธ์
cv2.imwrite("output_white_background.jpg", white_img)
