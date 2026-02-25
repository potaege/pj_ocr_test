import re
from rapidfuzz import process, fuzz

THAI_MONTHS = {
    "ม.ค.": "01", "มกราคม": "01",
    "ก.พ.": "02", "กุมภาพันธ์": "02",
    "มี.ค.": "03", "มีนาคม": "03",
    "เม.ย.": "04", "เมษายน": "04",
    "พ.ค.": "05", "พฤษภาคม": "05",
    "มิ.ย.": "06", "มิถุนายน": "06",
    "ก.ค.": "07", "กรกฎาคม": "07",
    "ส.ค.": "08", "สิงหาคม": "08",
    "ก.ย.": "09", "กันยายน": "09",
    "ต.ค.": "10", "ตุลาคม": "10",
    "พ.ย.": "11", "พฤศจิกายน": "11",
    "ธ.ค.": "12", "ธันวาคม": "12",
}

def convert_thai_date_ultimate(text: str, sep: str = "/"):
    if not isinstance(text, str):
        return "", False

    pattern = r'(\d{1,2})(.*?)(\d{4})'
    matches = re.findall(pattern, text)

    if not matches:
        return "", False

    for match in matches:
        day_raw, middle_raw, year_raw = match

        day = day_raw.zfill(2)
        year = year_raw

        month_clean = re.sub(r'(เดือน|คือน|เคือน|เดอน|พ\.ศ\.|พศ\.|พ\.|ศ\.|วันที่|\s+|\.)', '', middle_raw)

        if not month_clean:
            continue 

        choices = list(THAI_MONTHS.keys())
        best = process.extractOne(month_clean, choices, scorer=fuzz.WRatio)

        if best:
            best_key, score, _ = best
            
            if score >= 40: 
                month = THAI_MONTHS[best_key]
                
                # ==================================================
                # ✅ เพิ่มส่วนตรวจสอบความสมเหตุสมผลของวันที่ (Validation)
                # ==================================================
                is_valid = True
                
                # แปลงเป็น int เพื่อเช็คค่าตัวเลข
                day_int = int(day)
                month_int = int(month)
                
                # 1. เช็ควันที่: ต้องอยู่ระหว่าง 1 ถึง 31
                if day_int < 1 or day_int > 31:
                    is_valid = False
                    
                # 2. เช็คเดือน: ต้องอยู่ระหว่าง 1 ถึง 12 
                # (ถึงค่าจาก dict เราจะถูกเสมอ แต่เขียนดักไว้เป็น Best Practice ครับ)
                if month_int < 1 or month_int > 12:
                    is_valid = False
                # ==================================================
                
                # คืนค่าวันที่ที่ดึงได้ พร้อมสถานะ (True/False ตามที่เช็คได้)
                return f"{day}{sep}{month}{sep}{year}", is_valid

    return "", False