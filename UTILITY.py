import numpy as np
import re
def get_area_bracket(area):
    try:
        a = int(area)
        if a < 100:   return "Small"
        elif a < 200: return "Medium"
        else:          return "Large"
    except (ValueError, TypeError):
        return "Unknown"

def clean_area_list(area_list):
    cleaned = []
    for s in area_list:
        numeric_s = str(s).replace('m²', '').replace('sqm', '').replace('Sqm', '').strip()
        # If it's a range like '40 ~ 50', take the first number
        if '~' in numeric_s:
            numeric_s = numeric_s.split('~')[0].strip()
        if numeric_s:
            try:
                cleaned.append(int(numeric_s))
            except ValueError:
                cleaned.append(0)
        else:
            cleaned.append(0)
    return cleaned

def kde(d, r):
    if d <= r:
        return (1 - (d/r)**2)**2
    else:
        return 0

def get_bracket(price_val):
    try:
        p = float(price_val)
        if p < 3_000_000: return "Budget"
        elif p < 8_000_000: return "Mid-Range"
        else: return "Luxury"
    except (ValueError, TypeError):
        return "Unknown"

def clean_currency_list(currency_list):
    cleaned = []
    for s in currency_list:
        numeric_string = re.sub(r'[^\d.]', '', str(s))
        if numeric_string and numeric_string != '.':
            try:
                cleaned.append(int(float(numeric_string)))
            except ValueError:
                cleaned.append(0)
        else:
            cleaned.append(0)
    return cleaned