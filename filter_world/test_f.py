from rapidfuzz import process, fuzz

# 1. ข้อมูล Master Data (ลิสต์จังหวัดที่ถูกต้อง)
provinces = [
    "กรุงเทพมหานคร", "สมุทรปราการ", "ฉะเชิงเทรา", 
    "นครปฐม", "นนทบุรี", "ปทุมธานี"
]

# 2. ข้อมูลที่ได้จาก OCR (ซึ่งมักจะผิด)
ocr_results = [
    "กรงเทพ",           # เคส 1: สะกดผิด/สระหาย
    "จ.สมุทรปราการร",    # เคส 2: มีตัวอักษรเกิน/ขยะ
    "ฉะเชงเทราา"        # เคส 3: สระหายและตัวสะกดเกิน
]

print(f"{'ค่าจาก OCR':<18} | {'จังหวัดที่แมตช์':<15} | {'คะแนน':<6}")
print("-" * 45)

for text in ocr_results:
    # ใช้ process.extractOne เพื่อหาตัวที่ใกล้เคียงที่สุดเพียงตัวเดียว
    # scorer=fuzz.WRatio เป็นตัวที่สมดุลที่สุดสำหรับภาษาไทย
    match, score, index = process.extractOne(text, provinces, scorer=fuzz.WRatio)
    
    print(f"{text:<18} | {match:<15} | {score:.2f}%")