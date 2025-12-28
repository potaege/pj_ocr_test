import cv2

from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.mask_regions import mask_image_with_regions
from re_image.crop_regions import crop_regions 

REGIONS = {
    "citizen_id": (554, 82, 421, 54 ,False), ##พิกัดcrop 4ตัวหน้า แล้วตัวท้ายสุดคือ ต้องการให้ ภาพที่มีพื้นหลังสีอื่นทำให้กลายเป็นสีขาวไหม
    "name_lastname_th": (352, 147, 895, 89,False),
    "name_eng": (495, 240, 554, 54,False),
    "lastname_eng": (561, 293, 519, 47,False),
    "birthday": (550, 340, 279, 66,False),
    "religion": (529, 470, 122, 47,False),
    "address": (135, 511, 763, 121,True),
    "issue_date": (137, 632, 190, 38,False),
    "expiry_date": (700, 623, 192, 45,False),
}

def process_thai_id_image(image_path: str, output_txt="ocr_result.txt", raw_txt="ocr_raw.txt"):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    # 1) resize (ถ้าคุณยังต้องการ)
    img = resize_image(img, 1280, 800)

    # 2) crop ทีละช่อง + ใส่กรอบขาว
    crops = crop_regions(img, REGIONS, pad_x=35,pad_y=80,save_dir="debug_crops")

    results = {}
    raw_parts = []

    # 3) OCR ทีละช่อง
    for field, crop in crops.items():
        if crop is None:
            results[field] = ""
            continue

        is_addr = (field == "address") 
        res, used_api = run_ocr(crop , no_doc=is_addr, no_textline=is_addr)

        # เก็บ raw debug แยกตาม field
        raw_parts.append(f"\n=== {field} | API={used_api} ===\n")
        raw_parts.append(to_debug_string(res, max_chars=50000))

        texts = []
        collect_texts(res, texts)
        texts = [t for t in texts if len(t.strip()) >= 1]
        texts = unique_keep_order(texts)

        results[field] = " ".join(texts).strip()

    # 4) เขียน raw debug
    with open(raw_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(raw_parts))

    # 5) เขียนผลลัพธ์แบบ field: value
    with open(output_txt, "w", encoding="utf-8") as f:
        for k in REGIONS.keys():
            f.write(f"{k}: {results.get(k, '')}\n")

    print(f"✅ Done | saved={output_txt} | raw={raw_txt}")


if __name__ == "__main__":
    process_thai_id_image("image/thai_id/main_id.jpg")
