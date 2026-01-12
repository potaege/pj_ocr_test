import re

ENGLISH_MONTHS = {
    "Jan": "01", "January": "01",
    "Feb": "02", "February": "02",
    "Mar": "03", "March": "03",
    "Apr": "04", "April": "04",
    "May": "05", "May": "05",
    "Jun": "06", "June": "06",
    "Jul": "07", "July": "07",
    "Aug": "08", "August": "08",
    "Sep": "09", "September": "09",
    "Oct": "10", "October": "10",
    "Nov": "11", "November": "11",
    "Dec": "12", "December": "12",
}

def convert_english_date(text: str, sep: str = "/"):
    
    if not isinstance(text, str):
        return "", False

    text = text.strip()
    if not text:
        return "", False

    # เช็คว่าต้องมีตัวเลข และ ตัวอักษรภาษาอังกฤษ (a-z หรือ A-Z)
    if re.search(r"[a-zA-Z]", text) is None or re.search(r"\d", text) is None:
        return "", False

    parts = text.split()
    if len(parts) < 3:
        return "", False

    day, month_eng, year = parts[0], parts[1], parts[2]

    # วัน
    if not day.isdigit():
        return "", False

    day = day.zfill(2)

    # เดือน (แปลงตัวแรกเป็นพิมพ์ใหญ่ ที่เหลือพิมพ์เล็ก เพื่อให้ตรงกับ Key ใน Dict)
    # เช่น "january" -> "January", "JAN" -> "Jan"
    month = ENGLISH_MONTHS.get(month_eng.title()) 
    
    if not month:
        return "", False

    # ปี
    if not year.isdigit():
        return "", False

    # คืนค่า
    return f"{day}{sep}{month}{sep}{year}", True