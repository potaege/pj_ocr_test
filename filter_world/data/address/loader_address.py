import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # filter_world/
DATA_DIR = BASE_DIR / "data" / "address"

def load_thai_admin_data():
    with open(DATA_DIR / "provinces.json", encoding="utf-8") as f:
        provinces = json.load(f)

    with open(DATA_DIR / "districts.json", encoding="utf-8") as f:
        districts = json.load(f)

    with open(DATA_DIR / "sub_districts.json", encoding="utf-8") as f:
        sub_districts = json.load(f)

    return provinces, districts, sub_districts

def load_provinces():
    with open(DATA_DIR / "provinces.json", encoding="utf-8") as f:
        provinces = json.load(f)
    
    return provinces

def load_registration_offices():
    with open(DATA_DIR / "registration_offices.json", encoding="utf-8") as f:
        registration_offices = json.load(f)
    
    return registration_offices

def load_nationalities():
    with open(DATA_DIR / "nationalities.json", encoding="utf-8") as f:
        nationalities = json.load(f)
    
    return nationalities