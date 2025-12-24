import cv2

from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.mask_regions import mask_image_with_regions

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

def process_thai_id_image(
    image_path: str,
    output_txt="ocr_result.txt",
    raw_txt="ocr_raw.txt"
):
    # 1) โหลดภาพ
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    # 2) resize → 1280x800
    img = resize_image(img, 1280, 800)

    # 3) mask พื้นหลังขาว
    img = mask_image_with_regions(img, REGIONS)
    cv2.imwrite("output_white_background.jpg", img)

    # 4) OCR
    result, used_api = run_ocr(img)

    # debug raw
    with open(raw_txt, "w", encoding="utf-8") as f:
        f.write(f"USED_API={used_api}\n")
        f.write(to_debug_string(result))

    # 5) ดึงข้อความ
    texts = []
    collect_texts(result, texts)
    texts = [t for t in texts if len(t.strip()) >= 2]
    texts = unique_keep_order(texts)

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(texts))

    print(f"✅ Done | API={used_api} | lines={len(texts)}")

if __name__ == "__main__":
    process_thai_id_image("image/thai_id/thai_id.jpg")
