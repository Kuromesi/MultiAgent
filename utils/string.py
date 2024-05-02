import re

def filter_string(string: str) -> str:
    cleaned_s = re.sub(r'\s+', ' ', string).strip()
    return cleaned_s