from filter_world.help_filter.common import remove_prefix
from filter_world.help_filter.check_number_length import check_number_length
from filter_world.help_filter.thai_date import convert_thai_date # แก้
from filter_world.help_filter.eng_date import convert_english_date # แก้
from filter_world.help_filter.name_lastName_th import name_lastname_th
from filter_world.help_filter.name_lastName_eng import name_lastname_eng
from filter_world.help_filter.registrar__driving_license_thai import find_province_from_registrar
from filter_world.data.address.loader_address import load_provinces
PROVINCES = load_provinces()

import json
def receive_driving_license_thai_data(ocr_data: dict):

    result = dict(ocr_data)

    output_result = {}

    for k, v in result.items():
        result[k] = remove_prefix(v)

    car_type = result.get("car_type","") ## ยังไม่ได้ทำ
    car_id_1 , valid_car_id_1 = check_number_length(result.get("car_id1",""),8)
    car_id_2 , valid_car_id_2 = check_number_length(result.get("car_id2",""),8)
    issue_date_thai , valid_issue_date_thai = convert_thai_date(result.get("issue_date_thai",""))
    issue_date_eng , valid_issue_date_eng = convert_english_date(result.get("issue_date_eng",""))
    expiry_date_thai , valid_expiry_date_thai = convert_thai_date(result.get("expiry_date_thai",""))
    expiry_date_eng , valid_expiry_date_eng = convert_english_date(result.get("expiry_date_eng",""))
    prefix_name_th,name_th,last_name_th,valid_name_last_name_th = name_lastname_th(result.get("name_lastname_th", ""))
    prefix_name_eng,name_eng,last_name_eng,valid_name_last_name_eng = name_lastname_eng(result.get("name_lastName_eng", ""))
    birth_date_th , valid_birth_date_th = convert_thai_date(result.get("birth_date_th",""))
    birth_date_eng , valid_birth_date_eng = convert_english_date(result.get("birth_date_eng",""))
    thai_id, valid_thai_id = check_number_length(result.get("thai_id", ""),13)
    provinces , score_registrar ,nums_list , valid_registrar = find_province_from_registrar(result.get("registrar", ""),PROVINCES)

    output_result["car_type"] = car_type

    output_result["car_id_1"] = car_id_1
    output_result["valid_car_id_1"] = valid_car_id_1

    output_result["car_id_2"] = car_id_2
    output_result["valid_car_id_2"] = valid_car_id_2

    output_result["issue_date_thai"] = issue_date_thai
    output_result["valid_issue_date_thai"] = valid_issue_date_thai

    output_result["issue_date_eng"] = issue_date_eng
    output_result["valid_issue_date_eng"] = valid_issue_date_eng

    output_result["expiry_date_thai"] = expiry_date_thai
    output_result["valid_expiry_date_thai"] = valid_expiry_date_thai

    output_result["expiry_date_eng"] = expiry_date_eng
    output_result["valid_expiry_date_eng"] = valid_expiry_date_eng

    output_result['prefix_name_th'] = prefix_name_th
    output_result['name_th'] = name_th
    output_result['last_name_th'] = last_name_th
    output_result['valid_name_last_name_th'] = valid_name_last_name_th

    output_result['prefix_name_eng'] = prefix_name_eng
    output_result['name_eng'] = name_eng
    output_result['last_name_eng'] = last_name_eng
    output_result['valid_name_last_name_eng'] = valid_name_last_name_eng

    output_result["birth_date_th"] = birth_date_th
    output_result["valid_birth_date_th"] = valid_birth_date_th

    output_result["birth_date_eng"] = birth_date_eng
    output_result["valid_birth_date_eng"] = valid_birth_date_eng

    output_result["thai_id"] = thai_id 
    output_result["valid_thi_id"] = valid_thai_id

    output_result["provinces"] = provinces
    output_result["score_registrar"] = score_registrar
    output_result["nums_list"] = nums_list
    output_result["valid_registrar"] = valid_registrar

    return output_result






def main():
    
    ls = {
        'car_type': 'min general Private Car Diving Licencx(emporay)',
        'car_id1': 'min general 66005254', #
        'car_id2': 'min general 66005254', #
        'issue_date_thai': 'min general 24 เมษายน 2566', #
        'issue_date_eng': 'min general 24 April 2023', #
        'expiry_date_th': 'min general 24 เมษายน 2568', #
        'expiry_date_eng': 'min general 24 April 2025', #
        'name_lastname_th': 'min general นาย ตรีธวัฒน์ โชคกูลธวัฒน์', #
        'name_lastName_eng': 'min general MR TREETHAWAT CHOKKULTHAWAT : 4 5 1', #
        'birth_date_th': 'min general --2 มีนาคม 2547 -----', #
        'birth_date_eng': 'min general 22 March 2004', #
        'thai_id': 'min general 1 1043 00707 16 0', #
        'registrar': 'min general กรุงเnพมหานคร 4 Bangkok4' #
    }

    a = receive_driving_license_thai_data(ls)
    output_filter_txt = "results_filter_test"

    with open(output_filter_txt, "w", encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=2)
    


if __name__ == "__main__":
    main()