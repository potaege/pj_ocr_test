import re

def check_passport_no(text: str):
    if not isinstance(text, str):
        return "", False
    
    text = text.strip().upper()
    
    pattern = r'^[A-Z]{1,2}[0-9]{6,7}$'
    
    if re.match(pattern, text):
        return text, True
    else:
        return "", False