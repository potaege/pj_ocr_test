from filter_world.help_filter.common import remove_prefix
from filter_world.help_filter.height import check_height
from filter_world.help_filter.type import check_passport_type
from filter_world.help_filter.country_code import check_country_code
from filter_world.help_filter.passport_no import check_passport_no
from filter_world.help_filter.nationality_en import check_nationality_en
from filter_world.help_filter.check_number_length import check_number_length
from filter_world.help_filter.sex_en import check_sex_en
from filter_world.help_filter.height import check_height
from filter_world.help_filter.name_lastName_th import name_lastname_th
from filter_world.help_filter.name_eng import split_name_eng
from filter_world.help_filter.english_only import keep_english_words
from filter_world.help_filter.passport_province import parse_province_en
from filter_world.help_filter.eng_date import convert_english_date
from filter_world.data.address.loader_address import load_thai_admin_data
PROVINCES, DISTRICTS, SUB_DISTRICTS = load_thai_admin_data()

def receive_passport_ocr_data(ocr_data: dict):

    result = dict(ocr_data)

    output_result = {}

    for k, v in result.items():
        result[k] = remove_prefix(v)

    value_type, valid_type = check_passport_type(result.get("type", "")) # เช็คว่า type เป็นประเภทไหน (มี 4 ประเภท)
    value_country_code, valid_country_code = check_country_code(result.get("country_code", "")) # เช็คว่าเป็น THA หรือไม่
    value_passport_no, valid_passport_no = check_passport_no(result.get("passport_no", ""))
    last_name_en,valid_last_name_en = keep_english_words(result.get("last_name_en", ""))
    prefix_name_en,first_name_en,valid_first_name_en = split_name_eng(result.get("first_name_en", ""))
    prefix_name_th,name_th,last_name_th,valid_name_last_name_th = name_lastname_th(result.get("full_name_th", ""))
    nationality, valid_nationality = check_nationality_en(result.get("nationality", ""))
    date_of_birth, valid_date_of_birth = convert_english_date(result.get("date_of_birth", ""))
    identification_no, valid_identification_no = check_number_length(result.get("identification_no", ""), 13)
    sex, valid_sex = check_sex_en(result.get("sex", ""))
    height, valid_height = check_height(result.get("height", ""))
    place_of_birth, valid_place_of_birth = parse_province_en(result.get("place_of_birth", ""), PROVINCES)
    issue_date, valid_issue_date = convert_english_date(result.get("issue_date", ""))
    expiry_date, valid_expiry_date = convert_english_date(result.get("expiry_date", ""))


    output_result["type"] = value_type 
    output_result["type_valid"] = valid_type

    output_result["country_code"] = value_country_code
    output_result["country_code_valid"] = valid_country_code

    output_result["passport_no"] = value_passport_no
    output_result["passport_no_valid"] = valid_passport_no

    output_result['last_name_en'] = last_name_en
    output_result['valid_last_name_en'] = valid_last_name_en

    output_result['prefix_name_en'] = prefix_name_en
    output_result['first_name_en'] = first_name_en
    output_result['valid_first_name_en'] = valid_first_name_en

    output_result['prefix_name_th'] = prefix_name_th
    output_result['name_th'] = name_th
    output_result['last_name_th'] = last_name_th
    output_result['valid_name_last_name_th'] = valid_name_last_name_th

    output_result['nationality'] = nationality
    output_result['valid_nationality'] = valid_nationality

    output_result['identification_no'] = identification_no
    output_result['valid_identification_no'] = valid_identification_no

    output_result['date_of_birth'] = date_of_birth
    output_result['valid_date_of_birth'] = valid_date_of_birth

    output_result['sex'] = sex
    output_result['valid_sex'] = valid_sex

    output_result['height'] = height
    output_result['valid_height'] = valid_height

    output_result['place_of_birth'] = place_of_birth
    output_result['valid_place_of_birth'] = valid_place_of_birth

    output_result['issue_date'] = issue_date
    output_result['valid_issue_date'] = valid_issue_date

    output_result['expiry_date'] = expiry_date
    output_result['valid_expiry_date'] = valid_expiry_date

    print("📥 รับข้อมูลจาก passport แล้ว")
  
    return output_result

def main():

    ls = {
        'passport_no': 'XXXXXXX', # ผ่าน
        'country_code': 'XXXXXXX', # ผ่าน
        'type': 'XXXXXXX', # ผ่าน
        'last_name_en': 'XXXXXXX', # ผ่าน
        'first_name_en': 'XXXXXXX', # ผ่าน
        'full_name_th': 'XXXXXXX', # ผ่าน
        'nationality': 'XXXXXXX', # ผ่าน
        'date_of_birth': 'XXXXXXX', # ผ่าน
        'sex': 'XXXXXXX', # ผ่าน
        'height': 'XXXXXXX', # ผ่าน
        'place_of_birth': 'XXXXXXX', # ผ่าน
        'issue_date': 'XXXXXXX', # ผ่าน
        'expiry_date': 'XXXXXXX' # ผ่าน
    }

    a = receive_passport_ocr_data(ls)
    print(a)

if __name__ == "__main__":
    main()