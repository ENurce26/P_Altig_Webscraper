# Test Plan – Selenium Lead Automation

## Objective
Validate that the Selenium automation can successfully log in, navigate lead records, extract required fields, handle dynamic page states, and export structured output while identifying invalid or incomplete records.

## Scope
This test plan covers:
- login flow
- navigation to lead inbox
- lead record traversal
- popup handling
- gift certificate page skipping
- extraction of name, age, city, state, and phone numbers
- field normalization
- record validation
- CSV and summary output generation

## Test Environment
- Python
- Selenium WebDriver
- Firefox browser
- Dynamic web application requiring authenticated login

## Test Cases

| ID | Scenario | Expected Result |
|---|---|---|
| TC-01 | Valid login | User successfully reaches the application after authentication |
| TC-02 | Invalid login credentials | Login fails and no lead extraction occurs |
| TC-03 | Navigate to lead inbox | Lead inbox opens successfully |
| TC-04 | Gift certificate page encountered | Record is skipped and summary skip counter increments |
| TC-05 | Age popup appears | Popup closes and extraction continues |
| TC-06 | Missing name field | Record marked invalid with "Missing name" |
| TC-07 | Missing age field | Record marked invalid with "Missing age" |
| TC-08 | Missing city/state | Record marked invalid with location-related errors |
| TC-09 | Missing phone numbers | Record marked invalid with "No phone numbers found" |
| TC-10 | Valid phone number in raw 10-digit format | Phone is normalized to `(###) ###-####` |
| TC-11 | Lead extraction completes | Record is written to output CSV |
| TC-12 | Invalid record detected | Record is written to invalid records output |
| TC-13 | Run completes | Summary JSON is generated with execution metrics |

## Pass/Fail Criteria
- Pass: the automation completes the intended step and produces expected output or expected validation behavior
- Fail: the automation crashes, extracts incorrect values, skips required output, or does not report invalid data correctly

## Risks / Limitations
- UI selector changes may break extraction
- Browser timing and page load delays may affect reliability
- Authentication is required for full end-to-end execution