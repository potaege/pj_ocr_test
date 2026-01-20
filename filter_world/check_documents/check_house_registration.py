from filter_world.help_filter.common import remove_prefix
from filter_world.help_filter.house_no import check_house_no
from filter_world.help_filter.registry_office import check_registry_office
from filter_world.help_filter.house_type import check_house_type
from filter_world.help_filter.house_specification import check_house_specification
from filter_world.help_filter.thai_date import convert_thai_date
from filter_world.help_filter.address import parse_admin_from_address
from filter_world.data.address.loader_address import load_thai_admin_data
PROVINCES, DISTRICTS, SUB_DISTRICTS = load_thai_admin_data()
from filter_world.data.address.loader_address import load_registration_offices
REGISTRATION_OFFICES = load_registration_offices()

def receive_house_registration_ocr_data(ocr_data: dict):

    result = dict(ocr_data)

    output_result = {}

    for k, v in result.items():
        result[k] = remove_prefix(v)

    value_house_no, valid_house_no = check_house_no(result.get("house_no", ""))
    registry_office, valid_registry_office = check_registry_office(result.get("registry_office", ""), REGISTRATION_OFFICES)
    addr_rest, sub_th, dist_th, prov_th, addr_ok = parse_admin_from_address(
        result.get("address", ""),
        PROVINCES,
        DISTRICTS,
        SUB_DISTRICTS
    )
    # village_name, valid_village_name = keep_english_words(result.get("village_name", ""))
    # house_name, valid_house_name = keep_english_words(result.get("house_name", ""))
    house_type , valid_house_type = check_house_type(result.get("house_type", ""))
    house_specification, valid_house_specification = check_house_specification(result.get("house_specification", ""))
    date_of_registration, valid_date_of_registration = convert_thai_date(result.get("date_of_registration", ""))
    date_of_print_house_registration, valid_date_of_print_house_registration = convert_thai_date(result.get("date_of_print_house_registration", ""))

    output_result["house_no"] = value_house_no 
    output_result["house_no_valid"] = valid_house_no

    output_result['registry_office'] = registry_office
    output_result['registry_office_valid'] = valid_registry_office

    output_result["address_rest"] = addr_rest
    output_result["sub_district_th"] = sub_th
    output_result["district_th"] = dist_th
    output_result["province_th"] = prov_th
    output_result["address_valid"] = addr_ok

    # output_result['village_name'] = village_name
    # output_result['valid_village_name'] = valid_village_name

    # output_result['house_name'] = house_name
    # output_result['valid_house_name'] = valid_house_name
    
    output_result['house_type'] = house_type
    output_result['valid_house_type'] = valid_house_type

    output_result['house_specification'] = house_specification
    output_result['valid_house_specification'] = valid_house_specification

    output_result['date_of_registration'] = date_of_registration
    output_result['valid_date_of_registration'] = valid_date_of_registration

    output_result['date_of_print_house_registration'] = date_of_print_house_registration
    output_result['valid_date_of_print_house_registration'] = valid_date_of_print_house_registration

    print("📥 รับข้อมูลจาก house_registration แล้ว")
  
    return output_result

def main():
    
    ls = {
        "house_no": 'XXXXXXX',
        "registry_office": 'XXXXXXX',
        "address": 'XXXXXXX',
        "village_name": 'XXXXXXX',
        "house_name": 'XXXXXXX',
        "house_type": 'XXXXXXX',
        "house_specification": 'XXXXXXX',
        "date_of_registration": 'XXXXXXX',
        "date_of_print_house_registration": 'XXXXXXX'
        }
    
    a = receive_house_registration_ocr_data(ls)
    print(a)
    
if __name__ == "__main__":
    main()