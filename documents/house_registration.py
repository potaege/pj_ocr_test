import cv2

from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.mask_regions import mask_image_with_regions
from re_image.crop_regions import crop_regions 

# REGIONS = {
#     "้house_no":   (255, 110, 315, 70, True),
#     "registry_office":  (785, 110, 390, 70, True),
#     "address":          (165, 180, 870, 130, True),
#     "village_name":  (165, 330, 420, 70, True),
#     "house_name": (710, 330, 450, 70, True),
#     "house_type":  (165, 400, 420, 70, True),
#     "house_specification":   (765, 400, 450, 70, True),
#     "date_of_registration": (350, 480, 350, 60, True),
#     "date_of_print_house_registration": (950, 660, 270, 50, True),
# }

REGIONS = {
    "้house_no":   (255, 110, 315, 70, False),
    "registry_office":  (785, 110, 390, 70, False),
    "address":          (165, 180, 870, 130, True),
    "village_name":  (165, 330, 420, 70, False),
    "house_name": (710, 330, 450, 70, True),
    "house_type":  (165, 400, 420, 70, False),
    "house_specification":   (765, 400, 450, 70, False),
    "date_of_registration": (350, 480, 350, 60, False),
    "date_of_print_house_registration": (950, 660, 270, 50, False),
}

def process_house_registration_image(image_path: str, output_txt="ocr_result_house_registration.txt", raw_txt="ocr_raw_house_registration.txt"):
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
    process_house_registration_image("image/house_registration/01.png")
