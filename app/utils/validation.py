import re
from datetime import datetime
from typing import List, Dict

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_required_fields(data: Dict, required_fields: List[str]) -> Dict:
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields
    }

def validate_date_format(date_string: str, format: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False