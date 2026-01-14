import cv2
import json
from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.crop_regions import crop_regions 
from filter_world.check_documents.check_driving_license_thai import receive_driving_license_thai_data

REGIONS = {
    "car_type": (575, 77, 588, 49, True),          
    "car_id1": (467, 150, 273, 55, True),
    "car_id2": (839, 153, 320, 53, True),
    "issue_date_thai": (499, 210, 262, 45, True),
    "issue_date_eng": (515, 253, 192, 37, True),
    "expiry_date_thai": (929, 215, 262, 43, True),
    "expiry_date_eng": (945, 255, 196, 39, True),
    "name_lastname_th": (410, 339, 839, 83, True),
    "name_lastName_eng": (447, 422, 805, 100, True),
    "birth_date_th": (492, 523, 296, 60, True), ##
    "birth_date_eng": (502, 580, 256, 57, True),
    "thai_id": (760, 623, 393, 55, True),
    "registrar": (487, 698, 765, 68, True),
}

def driving_license_thai(image_path: str, output_txt="ocr_result.txt", raw_txt="ocr_raw.txt"):

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)
    
    img = resize_image(img, 1280, 800)

    crops = crop_regions(img, REGIONS, pad_x=35,pad_y=80,save_dir="debug_crops")

    results = {}
    raw_parts = []

    for field, crop in crops.items():
        if crop is None:
            results[field] = ""
            continue

        res, used_api = run_ocr(crop , False, False)

        raw_parts.append(f"\n=== {field} | API={used_api} ===\n")
        raw_parts.append(to_debug_string(res, max_chars=50000))

        texts = []
        collect_texts(res, texts)
        texts = [t for t in texts if len(t.strip()) >= 1]
        texts = unique_keep_order(texts)

        results[field] = " ".join(texts).strip()

    with open(raw_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(raw_parts))

    with open(output_txt, "w", encoding="utf-8") as f:
        for k in REGIONS.keys():
            f.write(f"{k}: {results.get(k, '')}\n")

    results_filter = receive_driving_license_thai_data(results)
    output_filter_txt = "results_filter"

    with open(output_filter_txt, "w", encoding="utf-8") as f:
        json.dump(results_filter, f, ensure_ascii=False, indent=2)

    print(f"✅ Done | saved={output_txt} | raw={raw_txt} | filter={output_filter_txt}")


if __name__ == "__main__":
    driving_license_thai("image/car_id.jpg")