import cv2
import json
from ocr.model import run_ocr
from ocr.utils import collect_texts, unique_keep_order, to_debug_string
from re_image.preprocess import resize_image
from re_image.crop_regions import crop_regions 
from filter_world.check_documents.check_thai_id import receive_thai_id_ocr_data
from test.test_output import evaluate_ocr_result

REGIONS = {
    "citizen_id": (554, 82, 421, 54 ,False), ##พิกัดcrop 4ตัวหน้า แล้วตัวท้ายสุดคือ ต้องการให้ ภาพที่มีพื้นหลังสีอื่นทำให้กลายเป็นสีขาวไหม
    "name_lastname_th": (355 ,149, 889, 93,True),
    "name_eng": (498, 251, 558, 54,True),
    "lastname_eng": (568, 293, 519, 47,True),
    "birthday": (550, 340, 279, 66,True),
    "religion": (529, 470, 122, 47,True),
    "address": (135, 511, 763, 121,True),
    "issue_date": (137, 632, 190, 38,True),
    "expiry_date": (700, 623, 192, 45,True),
}

ranks = {
    "citizen_id": 1,

    "prefix_name_th": 2,
    "last_name_th": 2,
    "prefix_name_eng": 2,
    "last_name_eng": 2,
    "province_th": 2,
    "issue_date": 2,
    "expiry_date": 2,

    "name_th": 3,
    "name_eng": 3,
    "birthday": 3,
    "district_th": 3,

    "sub_district_th": 4,

    "address_rest": 5,

    "religion": 6
}

disct = {
  "citizen_id": "", 
  "prefix_name_th": "นาย",   
  "name_th": "",  
  "last_name_th": "", 
  "prefix_name_eng": "Mr", 
  "name_eng": "",  
  "last_name_eng": "", 
  "birthday": "22/03/2547", 
  "religion": "พุทธ", 
  "address_rest": "", ## ที่อยู่ที่ คำที่มาก่อน พวก เขต แขวง จังหวัด 
  "sub_district_th": "รามอินทรา", 
  "district_th": "คันนายาว", 
  "province_th": "กรุงเทพมหานคร", 
  "issue_date": "07/04/2562", 
  "expiry_date": "21/03/2571" 
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

    

    results_filter = receive_thai_id_ocr_data(results)
    output_filter_txt = "results_filter"

    with open(output_filter_txt, "w", encoding="utf-8") as f:
        json.dump(results_filter, f, ensure_ascii=False, indent=2)

    print(f"✅ Done | saved={output_txt} | raw={raw_txt} | filter={output_filter_txt}")

    check_thai_id = evaluate_ocr_result(results_filter,disct,ranks)

    with open("ocr_result.json", "w", encoding="utf-8") as f:
        json.dump(check_thai_id, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    process_thai_id_image("image/thai_id/real_main_id.jpg")
