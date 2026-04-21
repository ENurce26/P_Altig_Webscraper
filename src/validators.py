import re

PHONE_NUMBER_PATTERN = re.compile(r'(\(\d{3}\)\s\d{3}-\d{4})|(\d{10})')
NAME_PATTERN = re.compile(r'(\w+),\s(\w+)')
CITY_STATE_PATTERN = re.compile(r"([^,]+),\s*([A-Za-z]+)")


def extract_name(name_html: str) -> str:
    match = NAME_PATTERN.search(name_html or "")
    if match:
        return f"{match.group(1)}, {match.group(2)}"
    return "N/A"


def extract_city_state(address_text: str) -> tuple[str, str]:
    match = CITY_STATE_PATTERN.search(address_text or "")
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "N/A", "N/A"


def extract_age(age_text: str) -> str:
    match = re.search(r'\(Age: (\d+)\)', age_text or "")
    if match:
        return match.group(1)
    return "N/A"


def normalize_phone(raw_number: str) -> str | None:
    if not raw_number:
        return None

    raw_number = raw_number.strip()

    if PHONE_NUMBER_PATTERN.match(raw_number):
        if len(raw_number) == 10 and raw_number.isdigit():
            return f"({raw_number[0:3]}) {raw_number[3:6]}-{raw_number[6:]}"
        return raw_number

    return None

def validate_record(record: dict) -> dict:
    errors = []

    name = record.get("Name", "N/A")
    age = record.get("Age", "N/A")
    city = record.get("City", "N/A")
    state = record.get("State", "N/A")
    phones = record.get("Phones", [])

    if name == "N/A":
        errors.append("Missing name")

    if age == "N/A":
        errors.append("Missing age")
    elif not str(age).isdigit():
        errors.append("Age is not numeric")

    if city == "N/A":
        errors.append("Missing city")

    if state == "N/A":
        errors.append("Missing state")

    if not phones:
        errors.append("No phone numbers found")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }