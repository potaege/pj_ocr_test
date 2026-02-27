from filter_world.help_filter.check_number_length import check_number_length
from filter_world.help_filter.common import remove_prefix
from filter_world.help_filter.name_lastName_th import name_lastname_th
from filter_world.help_filter.identification_no import check_identification_no
from filter_world.help_filter.house_no import check_house_no
from filter_world.help_filter.registry_office import check_registry_office
from filter_world.help_filter.sex_th import check_sex_th
from filter_world.help_filter.nationality_th import check_nationality_th
from filter_world.help_filter.thai_date_spec import convert_thai_date_ultimate
from filter_world.help_filter.birth_delivery_person import check_birth_delivery_person
from filter_world.help_filter.address import parse_admin_from_address
from filter_world.help_filter.born_certification_province import parse_province_th
from filter_world.help_filter.born_certification_country import parse_countries_th
from filter_world.data.address.loader_address import load_thai_admin_data
PROVINCES, DISTRICTS, SUB_DISTRICTS = load_thai_admin_data()
from filter_world.data.address.loader_address import load_countries
COUNTRIES = load_countries()
from filter_world.data.address.loader_address import load_registration_offices
REGISTRATION_OFFICES = load_registration_offices()

def receive_born_certification_ocr_data(ocr_data: dict):

    result = dict(ocr_data)

    output_result = {}

    for k, v in result.items():
        result[k] = remove_prefix(v)

    prefix_name_th,name_th,last_name_th,valid_name_last_name_th = name_lastname_th(result.get("full_name_th", ""))
    identification_no, valid_identification_no = check_identification_no(result.get("identification_no", ""))
    sex, valid_sex = check_sex_th(result.get("sex", ""))
    nationality, valid_nationality = check_nationality_th(result.get("nationality", ""))
    date_of_birth, valid_date_of_birth = convert_thai_date_ultimate(result.get("date_of_birth", ""))
    place_of_birth_rest, sub_th, dist_th, prov_th, addr_ok = parse_admin_from_address(
        result.get("place_of_birth", ""),
        PROVINCES,
        DISTRICTS,
        SUB_DISTRICTS
    )
    being_the_child_no, valid_being_the_child_no = check_number_length(result.get("being_the_child_no", ""),1)
    birth_delivery_person, valid_birth_delivery_person = check_birth_delivery_person(result.get("birth_delivery_person", ""))
    weight_at_birth, valid_weight_at_birth = check_number_length(result.get("weight_at_birth", ""),4)
    house_registration_add, valid_house_registration_add = check_house_no(result.get("house_registration_add", ""))
    prefix_mother_name_th,mother_name_th,mother_last_name_th,valid_mother_name_last_name_th = name_lastname_th(result.get("mother_name_th", ""))
    mother_identification_no, valid_mother_identification_no = check_identification_no(result.get("mother_identification_no", ""))
    mother_province_of_birth, valid_mother_province_of_birth = parse_province_th(result.get("mother_province_of_birth", ""), PROVINCES)
    mother_country_of_birth, valid_mother_country_of_birth = parse_countries_th(result.get("mother_country_of_birth", ""), COUNTRIES)
    prefix_father_name_th,father_name_th,father_last_name_th,valid_father_name_last_name_th = name_lastname_th(result.get("father_name_th", ""))
    father_identification_no, valid_father_identification_no = check_identification_no(result.get("father_identification_no", ""))    
    father_province_of_birth, valid_father_province_of_birth = parse_province_th(result.get("father_province_of_birth", ""), PROVINCES)
    father_country_of_birth, valid_father_country_of_birth = parse_countries_th(result.get("father_country_of_birth", ""), COUNTRIES)                                                                                
    registry_office, valid_registry_office = check_registry_office(result.get("registry_office", ""), REGISTRATION_OFFICES)
    date_of_birth_registration, valid_date_of_birth_registration = convert_thai_date_ultimate(result.get("date_of_birth_registration", ""))

    output_result['prefix_name_th'] = prefix_name_th
    output_result['name_th'] = name_th
    output_result['last_name_th'] = last_name_th
    output_result['valid_name_last_name_th'] = valid_name_last_name_th

    output_result['identification_no'] = identification_no
    output_result['identification_no_valid'] = valid_identification_no

    output_result['sex'] = sex
    output_result['sex_valid'] = valid_sex

    output_result['nationality'] = nationality
    output_result['nationality_valid'] = valid_nationality

    output_result['date_of_birth'] = date_of_birth
    output_result['date_of_birth_valid'] = valid_date_of_birth

    output_result["place_of_birth_rest"] = place_of_birth_rest
    output_result["sub_district_th"] = sub_th
    output_result["district_th"] = dist_th
    output_result["province_th"] = prov_th
    output_result["address_valid"] = addr_ok

    output_result['being_the_child_no'] = being_the_child_no
    output_result['being_the_child_no_valid'] = valid_being_the_child_no

    output_result['birth_delivery_person'] = birth_delivery_person
    output_result['birth_delivery_person_valid'] = valid_birth_delivery_person

    output_result['weight_at_birth'] = weight_at_birth
    output_result['weight_at_birth_valid'] = valid_weight_at_birth

    output_result['house_registration_add'] = house_registration_add
    output_result['house_registration_add_valid'] = valid_house_registration_add

    output_result['prefix_mother_name_th'] = prefix_mother_name_th
    output_result['mother_name_th'] = mother_name_th
    output_result['mother_last_name_th'] = mother_last_name_th
    output_result['valid_mother_name_last_name_th'] = valid_mother_name_last_name_th

    output_result['mother_identification_no'] = mother_identification_no
    output_result['mother_identification_no_valid'] = valid_mother_identification_no

    output_result['mother_province_of_birth'] = mother_province_of_birth
    output_result['mother_province_of_birth_valid'] = valid_mother_province_of_birth

    output_result['mother_country_of_birth'] = mother_country_of_birth
    output_result['mother_country_of_birth_valid'] = valid_mother_country_of_birth

    output_result['prefix_father_name_th'] = prefix_father_name_th
    output_result['father_name_th'] = father_name_th
    output_result['father_last_name_th'] = father_last_name_th
    output_result['valid_father_name_last_name_th'] = valid_father_name_last_name_th

    output_result['father_identification_no'] = father_identification_no
    output_result['father_identification_no_valid'] = valid_father_identification_no

    output_result['father_province_of_birth'] = father_province_of_birth
    output_result['father_province_of_birth_valid'] = valid_father_province_of_birth

    output_result['father_country_of_birth'] = father_country_of_birth
    output_result['father_country_of_birth_valid'] = valid_father_country_of_birth

    output_result['registry_office'] = registry_office
    output_result['registry_office_valid'] = valid_registry_office

    output_result['date_of_birth_registration'] = date_of_birth_registration
    output_result['date_of_birth_registration_valid'] = valid_date_of_birth_registration

    print("📥 รับข้อมูลจาก born_certification แล้ว")
  
    return output_result

def main():
    
    ls = {
    "full_name_th":               'XXXXXXX', # ผ่าน
    "identification_no":          'XXXXXXX', # ผ่าน
    "sex":                        'XXXXXXX', # ผ่าน
    "nationality":                'XXXXXXX', # ผ่าน
    "date_of_birth":              'XXXXXXX', # ผ่าน
    "place_of_birth":             'XXXXXXX', # ผ่าน
    "being_the_child_no":         'XXXXXXX', # ผ่าน
    "birth_delivery_person":      'XXXXXXX', # ผ่าน
    "weight_at_birth":            'XXXXXXX', # ผ่าน
    "house_registration_add":     'XXXXXXX', # ผ่าน
    "mother_name_th":             'XXXXXXX', # ผ่าน
    "mother_identification_no":   'XXXXXXX', # ผ่าน
    "mother_province_of_birth":   'XXXXXXX', # ผ่าน
    "mother_country_of_birth":    'XXXXXXX', # ผ่าน
    "father_name_th":             'XXXXXXX', # ผ่าน
    "father_identification_no":   'XXXXXXX', # ผ่าน
    "father_province_of_birth":   'XXXXXXX', # ผ่าน
    "father_country_of_birth":    'XXXXXXX', # ผ่าน
    "registry_office":            'XXXXXXX', # ผ่าน
    "date_of_birth_registration": 'XXXXXXX', # ผ่าน
    }
    
    a = receive_born_certification_ocr_data(ls)
    print(a)
    
if __name__ == "__main__":
    main()