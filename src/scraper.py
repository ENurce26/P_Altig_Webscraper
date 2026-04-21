from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import re
import time

from config import BASE_URL
import logging
from validators import extract_name, extract_city_state, extract_age, normalize_phone, validate_record

def safe_click(driver, selector, retries=2, delay=2):
    for attempt in range(retries):
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            logging.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logging.warning(f"Click failed (attempt {attempt+1}) for {selector}: {e}")
            time.sleep(delay)

    logging.error(f"Failed to click element after {retries} attempts: {selector}")
    return False


def create_driver():
    logging.info("Creating Firefox WebDriver.")
    try:
        return webdriver.Firefox()
    except WebDriverException:
        print("Opening Firefox didn't work, try rerunning the script.")
        raise


def navigate_and_login(user, password, driver):
    logging.info("Navigating to login page.")
    driver.get(BASE_URL)
    time.sleep(3)

    driver.find_element(By.CSS_SELECTOR, "#Alias").send_keys(user)
    driver.find_element(By.CSS_SELECTOR, "#Password").send_keys(password + Keys.ENTER)
    logging.info("Login submitted.")
    time.sleep(3)


def scrape_leads(driver):
    people_data = []
    invalid_records = []

    summary = {
        "total_leads_detected": 0,
        "records_collected": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "gift_certificate_skips": 0,
        "navigation_errors": 0
    }

    try:
        if not safe_click(driver, ".list-group-item:nth-child(2)"):
            summary["navigation_errors"] += 1
            return {
                "records": people_data,
                "invalid_records": invalid_records,
                "summary": summary
            }
        time.sleep(3)
    except Exception:
        print("Unable to navigate to Lead Inbox.")
        logging.error("Unable to navigate to Lead Inbox.")

    driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2)").click()
    time.sleep(4)

    first_entry = driver.find_element(By.CSS_SELECTOR, "a[href^='/Lead/InboxDetail?LeadId=']")
    first_entry.click()
    time.sleep(3)

    viewing_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-5.text-center").text
    numbers = re.findall(r'\d+', viewing_text)
    total_leads = int(numbers[1])
    summary["total_leads_detected"] = total_leads
    logging.info(f"Detected {total_leads} total leads.")

    for _ in range(total_leads):
        gift_certificate_elements = driver.find_elements(By.CSS_SELECTOR, "div.certificate-template")
        if gift_certificate_elements:
            print("Gift certificate page detected, skipping...")
            summary["gift_certificate_skips"] += 1
            logging.warning("Gift certificate page detected, skipping lead.")
            try:
                if not safe_click(driver, "button[onclick*='/Lead/MoveNext']"):
                    summary["navigation_errors"] += 1
                    logging.error("Failed to click next lead button.")
                    break
                time.sleep(4)
                continue
            except Exception as e:
                print(f"Failed to move to the next lead: {e}")
                summary["navigation_errors"] += 1
                logging.error(f"Failed to move to next lead after gift certificate page: {e}")
                break

        person_info = {'Phones': set()}

        try:
            WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.btn.btn-secondary[onclick*='ClosePopup']")
                )
            ).click()
            print("Popup closed.")
            time.sleep(2)
        except (NoSuchElementException, TimeoutException, AttributeError):
            print("No popup present.")

        try:
            name_html = driver.find_element(
                By.CSS_SELECTOR,
                "h4.list-group-item-heading.f-18.m-b-sm.m-t-0"
            ).get_attribute('innerHTML')
            person_info['Name'] = extract_name(name_html)
        except Exception as e:
            print(f"An error occurred: {e}. Name wasn't found.")
            person_info['Name'] = 'N/A'

        try:
            address_text = driver.find_element(
                By.XPATH,
                "(//p[contains(@class, 'list-group-item-text f-12')]/b)[2]"
            ).text
            city, state = extract_city_state(address_text)
            person_info['City'] = city
            person_info['State'] = state
        except Exception as e:
            print(f"An error occurred: {e}. Address wasn't found.")
            person_info['City'] = 'N/A'
            person_info['State'] = 'N/A'

        try:
            age_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-9 > span:nth-of-type(2)").text
            person_info['Age'] = extract_age(age_text)
        except Exception as e:
            print(f"An error occurred: {e}. Age wasn't found.")
            person_info['Age'] = 'N/A'

        try:
            call_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.btn.btn-sm.btn-primary.w-100[onclick*='OpenPhoneDiv']")
                )
            )
            call_button.click()
            call_phone_number_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-7")
            for elem in call_phone_number_elements:
                formatted_phone = normalize_phone(elem.text)
                if formatted_phone:
                    person_info['Phones'].add(formatted_phone)
        except Exception as e:
            print(f"An error occurred {e}. Call button wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")

        try:
            initial_phone_elements = driver.find_elements(
                By.CSS_SELECTOR,
                "div.col-xs-6 > span:nth-child(2), div.col-xs-12 > span:nth-child(2)"
            )
            for elem in initial_phone_elements:
                formatted_phone = normalize_phone(elem.text)
                if formatted_phone:
                    person_info['Phones'].add(formatted_phone)
        except Exception as e:
            print(f"An error occurred {e}. Primary number wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")

        try:
            more_buttons = driver.find_elements(By.ID, "ShowHideMoreButton")
            if more_buttons:
                more_buttons[0].click()
                time.sleep(1)
                additional_phone_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.col-xs-6 > span:nth-child(2), div.col-xs-12 > span:nth-child(2)"
                )
                for elem in additional_phone_elements:
                    formatted_phone = normalize_phone(elem.text)
                    if formatted_phone:
                        person_info['Phones'].add(formatted_phone)
        except Exception as e:
            print(f"An error occurred {e}. More button wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")

        person_info['Phones'] = list(person_info['Phones'])

        validation_result = validate_record(person_info)

        people_data.append(person_info)
        summary["records_collected"] += 1

        if validation_result["is_valid"]:
            summary["valid_records"] += 1
            logging.info(f"Valid record collected for {person_info.get('Name', 'Unknown')}")
        else:
            summary["invalid_records"] += 1
            invalid_records.append({
                "record": person_info,
                "errors": validation_result["errors"]
            })
            logging.warning(
                f"Invalid record for {person_info.get('Name', 'Unknown')}: "
                f"{'; '.join(validation_result['errors'])}"
            )

        viewing_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-5.text-center").text
        numbers = re.findall(r'\d+', viewing_text)
        current_lead = int(numbers[0])

        if current_lead == total_leads:
            break

        if not safe_click(driver, "button[onclick*='/Lead/MoveNext']"):
            summary["navigation_errors"] += 1
            logging.error("Failed to navigate to next lead.")
            break
        time.sleep(4)

    return {
    "records": people_data,
    "invalid_records": invalid_records,
    "summary": summary
}