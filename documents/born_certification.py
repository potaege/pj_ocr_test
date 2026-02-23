import cv2
import json
from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.mask_regions import mask_image_with_regions
from re_image.crop_regions import crop_regions
from filter_world.check_documents.check_born_certification import receive_born_certification_ocr_data

REGIONS = {
    "full_name_th":               (59, 258, 467, 63, False),
    "identification_no":          (529, 192, 267, 65, False),
    "sex":                        (529, 261, 81, 61, False),
    "nationality":                (611, 261, 185, 61, False),
    "date_of_birth":              (155, 323, 285, 36, False),
    "place_of_birth":             (155, 361, 466, 84, False),
    "house_registration_add":     (588, 494, 205, 99, False),
    "mother_name_th":             (59, 595, 467, 62, False),
    "mother_identification_no":   (529, 595, 176, 63, False),
    "father_name_th":             (59, 784, 467, 62, False),
    "father_identification_no":   (529, 784, 176, 63, False),
    "registry_office":            (3, 205, 523, 51, False),
    "date_of_birth_registration": (529, 1243, 268, 39, False),
}

def process_born_certification_image(image_path: str, output_txt="ocr_result_born_certification.txt", raw_txt="ocr_raw_born_certification.txt"):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    # 1) resize (ถ้าคุณยังต้องการ)
    img = resize_image(img, 800, 1280)
    cv2.imwrite("debug_crops/resized_image.png", img)

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

    # results_filter = receive_born_certification_ocr_data(results)
    # output_filter_born_certification = "results_filter_born_certification"

    # with open(output_filter_born_certification, "w", encoding="utf-8") as f:
    #     json.dump(results_filter, f, ensure_ascii=False, indent=2)

    # print(f"✅ Done | saved={output_txt} | raw={raw_txt} | filter={output_filter_born_certification}")

if __name__ == "__main__":
    process_born_certification_image("image/born_certification/01.jpg")
