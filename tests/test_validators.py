from src.validators import validate_record

def test_valid_record():
    record = {
        "Name": "Smith, John",
        "Age": "32",
        "City": "Cleveland",
        "State": "OH",
        "Phones": ["(216) 555-1234"]
    }

    result = validate_record(record)
    assert result["is_valid"] is True


def test_missing_name():
    record = {
        "Name": "N/A",
        "Age": "32",
        "City": "Cleveland",
        "State": "OH",
        "Phones": ["(216) 555-1234"]
    }

    result = validate_record(record)
    assert result["is_valid"] is False
    assert "Missing name" in result["errors"]