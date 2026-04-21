# Selenium Lead Automation

A Selenium-based browser automation project that logs into a lead management platform, navigates lead records, extracts structured contact data, validates extracted fields, and exports results to CSV.

## Purpose
This project was built to replace a manual lead collection workflow with a repeatable browser automation process. In addition to data extraction, the project performs field normalization, record validation, invalid-record tracking, and run summary reporting.

## Features
- Automated login and navigation through a dynamic web interface
- Extraction of name, age, city, state, and phone numbers
- Phone number normalization
- Record-level validation for missing or malformed fields
- Invalid record tracking with error reporting
- CSV export for collected records
- Execution summary output
- Logging for traceability and troubleshooting

## Tech Stack
- Python
- Selenium
- Regular expressions
- CSV / JSON output
- Logging

## Project Structure
```text
selenium-lead-automation/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── main.py
│   ├── config.py
│   ├── scraper.py
│   ├── validators.py
│   └── utils.py
├── docs/
│   └── test-plan.md
├── tests/
├── output/
└── logs/
```

## QA Scenarios Considered
- missing required fields
- invalid phone number formatting
- popup interruption during extraction
- gift certificate pages that should be skipped
- page navigation failures
- records with no available phone numbers

## Design Decisions
- Validation logic was separated from scraping logic to improve maintainability and make record-level checks easier to test
- Invalid records are stored separately to support defect visibility and downstream review
- Summary metrics are generated to provide a lightweight execution report after each run

## Example Execution Output

### Run Summary
```json
{
    "total_leads_detected": 25,
    "records_collected": 22,
    "valid_records": 18,
    "invalid_records": 4,
    "gift_certificate_skips": 2,
    "navigation_errors": 1
}
```

## Key QA Engineering Concepts Demonstrated

- Separation of concerns (scraping vs validation vs output)
- Data validation and defect detection
- Handling dynamic UI states (popups, missing elements, navigation errors)
- Logging and traceability for debugging
- Execution reporting via summary metrics
- Identification and tracking of invalid records