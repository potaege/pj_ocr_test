import re

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

def convert_thai_date(text: str, sep: str = "/"):
   
    if not isinstance(text, str):
        return "", False

    text = text.strip()
    if not text:
        return "", False

    # ต้องมีตัวเลขและอักษรไทย
    if re.search(r"[ก-๙]", text) is None or re.search(r"\d", text) is None:
        return "", False

    parts = text.split()
    if len(parts) < 3:
        return "", False

    day, month_th, year = parts[0], parts[1], parts[2]

    # วัน
    if not day.isdigit():
        return "", False

    day = day.zfill(2)

    # เดือน
    month = THAI_MONTHS.get(month_th)
    if not month:
        return "", False

    # ปี
    if not year.isdigit():
        return "", False

    # คืนค่า
    return f"{day}{sep}{month}{sep}{year}", True
