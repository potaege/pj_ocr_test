from filter_world.help_filter.common import remove_prefix
from filter_world.help_filter.check_number_length import check_number_length
from filter_world.help_filter.name_lastName_th import name_lastname_th
from filter_world.help_filter.name_eng import split_name_eng
from filter_world.help_filter.english_only import keep_english_words
from filter_world.help_filter.thai_date import convert_thai_date
from filter_world.help_filter.religion_th import normalize_religion_th
from filter_world.help_filter.address import parse_admin_from_address
from filter_world.data.address.loader_address import load_thai_admin_data
PROVINCES, DISTRICTS, SUB_DISTRICTS = load_thai_admin_data()

def receive_thai_id_ocr_data(ocr_data: dict):

    result = dict(ocr_data)

    output_result = {}

    for k, v in result.items():
        result[k] = remove_prefix(v)

    value_thai_id, valid_thai_id = check_number_length(result.get("citizen_id", ""),13)
    prefix_name_th,name_th,last_name_th,valid_name_last_name_th = name_lastname_th(result.get("name_lastname_th", ""))
    prefix_name_eng,name_eng,valid_name_eng = split_name_eng(result.get("name_eng", ""))
    last_name_eng,valid_last_name_eng = keep_english_words(result.get("lastname_eng", ""))
    birthday , valid_birthday = convert_thai_date(result.get("birthday", ""))
    religion, valid_religion = normalize_religion_th(result.get("religion", ""))
    ## ที่อยู่
    addr_rest, sub_th, dist_th, prov_th, addr_ok = parse_admin_from_address(
        result.get("address", ""),
        PROVINCES,
        DISTRICTS,
        SUB_DISTRICTS
    )

    issue_date, valid_issue_date = convert_thai_date(result.get("issue_date", ""))
    expiry_date, valid_expiry_date = convert_thai_date(result.get("expiry_date", ""))


    output_result["citizen_id"] = value_thai_id 
    output_result["citizen_id_valid"] = valid_thai_id

    output_result['prefix_name_th'] = prefix_name_th
    output_result['name_th'] = name_th
    output_result['last_name_th'] = last_name_th
    output_result['valid_name_last_name_th'] = valid_name_last_name_th

    output_result['prefix_name_eng'] = prefix_name_eng
    output_result['name_eng'] = name_eng
    output_result['valid_name_eng'] = valid_name_eng

    output_result['last_name_eng'] = last_name_eng
    output_result['valid_last_name_eng'] = valid_last_name_eng

    output_result['birthday'] = birthday
    output_result['valid_birthday'] = valid_birthday

    output_result['religion'] = religion
    output_result['valid_religion'] = valid_religion

    ##ที่อยู่
    output_result["address_rest"] = addr_rest
    output_result["sub_district_th"] = sub_th
    output_result["district_th"] = dist_th
    output_result["province_th"] = prov_th
    output_result["address_valid"] = addr_ok

    output_result['issue_date'] = issue_date
    output_result['valid_issue_date'] = valid_issue_date

    output_result['expiry_date'] = expiry_date
    output_result['valid_expiry_date'] = valid_expiry_date




    print("📥 รับข้อมูลจาก thai_id แล้ว")
  
    return output_result

def main():

    ls = {''
        'citizen_id': 'min general 1 1043 00707 16 0',
        'name_lastname_th': 'min general [าย ตรีธวัฒน์ โชคกูลธวัฒน์',
        'name_eng': 'min general Mr. Treethawat',
        'lastname_eng': 'min general Chokkulthawat',
        'birthday': 'min general 22 มี.ค. 2547',
        'religion': 'min general guเ',
        'address': 'min general ที่อยู130 ถ.คู้บอน แขวงรามอินทรา เขตคันนายาว กรงเทพมหานคร - −', ## เหลืออันนี้
        'issue_date': 'min general 7 เม.ย. 2562',
        'expiry_date': 'min general 21 มี.ค. 2571'
        }
    a = receive_thai_id_ocr_data(ls)
    print(a)
    


if __name__ == "__main__":
    main()