from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import pandas as pd
import re
import csv

user = ""
password = ""

phone_number_pattern = re.compile(r'(\(\d{3}\)\s\d{3}-\d{4})|(\d{10})')
name_pattern = re.compile(r'(\w+),\s(\w+)')
city_state_pattern = re.compile(r"([^,]+),\s*([A-Za-z]+)")

# Initialize WebDriver, Replace with another browser if needed
try:
    driver = webdriver.Firefox()
except WebDriverException:
    print("Opening Firefox didn't work, try rerunning the script. If still not working, call Eri")
    exit(1)

def navigate_and_login(user, password, driver):
    driver.get("https://m.planetaltig.com/")
    time.sleep(3)

    # Login
    driver.find_element(By.CSS_SELECTOR, "#Alias").send_keys(user)
    driver.find_element(By.CSS_SELECTOR, "#Password").send_keys(password + Keys.ENTER)
    time.sleep(3)

def scrape_leads(driver):
    people_data = []

    # Navigate to "Lead Inbox"
    try:
        driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2)").click()
        time.sleep(3)
    except Exception as e:
        print("Unable to navigate to Lead Inbox.")

    # (1) = My Schedule, (2) = All leads, (3) = In-Town, (4) = Road Trip, (5) = List Lead, etc.
    driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2)").click()
    time.sleep(4)
    
    # Click on the first entry in the table
    first_entry = driver.find_element(By.CSS_SELECTOR, "a[href^='/Lead/InboxDetail?LeadId=']")
    first_entry.click()
    time.sleep(3)

    # Get the total number of leads from the "viewing x/y" element
    viewing_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-5.text-center").text
    # Use regular expression to find the numbers in "viewing 1/100". this puts 1 and 100 into a list
    numbers = re.findall(r'\d+', viewing_text)
    total_leads = int(numbers[1])

    # Loop through all leads
    for _ in range(total_leads):
        # Check for gift certificate page
        gift_certificate_elements = driver.find_elements(By.CSS_SELECTOR, "div.certificate-template")
        if gift_certificate_elements:
            print("Gift certificate page detected, skipping...")
            # Code to move to the next lead without adding 'N/A' entry
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='/Lead/MoveNext']")
                next_button.click()
                time.sleep(4)
                continue  # Skip the rest of the loop and proceed with the next iteration
            except Exception as e:
                print(f"Failed to move to the next lead: {e}")
                break  # Exit the loop if unable to find or click the next button


        person_info = {'Phones': set()}

        try:
        # Check if the age popup is present and close it if so
            close_button = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-secondary[onclick*='ClosePopup']"))).click()
            print("Popup closed.")
            time.sleep(2)
        except(NoSuchElementException, TimeoutException,AttributeError):
            print("No popup present.")

        # Extract the name
        try:
            name_element_html = driver.find_element(By.CSS_SELECTOR, "h4.list-group-item-heading.f-18.m-b-sm.m-t-0").get_attribute('innerHTML')
            name_match = name_pattern.search(name_element_html)
            if name_match:
                person_info['Name'] = f"{name_match.group(1)}, {name_match.group(2)}"
            else:
                person_info['Name'] = 'N/A'
        except Exception as e:
            print("An error occured: {e}. Name wasn't found.")
            person_info['Name'] = 'N/A'

        # Extract the city and state from the address
        try:
            address_text = driver.find_element(By.XPATH, "(//p[contains(@class, 'list-group-item-text f-12')]/b)[2]").text
            match = city_state_pattern.search(address_text)
            if match:
                person_info['City'] = match.group(1).strip()
                person_info['State'] = match.group(2).strip()
            else:
                person_info['City'] = 'N/A'
                person_info['State'] = 'N/A'
        except Exception as e:
            print(f"An error occurred: {e}. Address wasn't found.")
            person_info['City'] = 'N/A'
            person_info['State'] = 'N/A'


        # Extract the age
        try:
            age_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-9 > span:nth-of-type(2)").text
            person_info['Age'] = re.search(r'\(Age: (\d+)\)', age_text).group(1)
        except Exception as e:
            print(f"An error occured: {e}. Age wasn't found.")
            person_info['Age'] = 'N/A'


        try:
            call_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-sm.btn-primary.w-100[onclick*='OpenPhoneDiv']")))
            call_button.click()
            call_phone_number_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-7")
            for elem in call_phone_number_elements:
                if phone_number_pattern.match(elem.text):
                    # Transform the phone number to the desired format
                    raw_number = elem.text
                    if len(raw_number) == 10 and raw_number.isdigit():  # Checks if the format is XXXXXXXXXX
                        formatted_number = f"({raw_number[0:3]}) {raw_number[3:6]}-{raw_number[6:]}"
                        person_info['Phones'].add(formatted_number)
                    else:
                        person_info['Phones'].add(raw_number)  # Add the number without formatting if it doesn't match the criteria
        except Exception as e:
            print(f"An error occurred {e}. Call button wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")


        try:
            initial_phone_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-6 > span:nth-child(2), div.col-xs-12 > span:nth-child(2)")
            for elem in initial_phone_elements:
                if phone_number_pattern.match(elem.text):
                    person_info['Phones'].add(elem.text)
        except Exception as e:
            print(f"An error occured {e}. Primary number wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")

   
        # If there is a 'More' button, click it to show more phone numbers
        try:
            more_buttons = driver.find_elements(By.ID, "ShowHideMoreButton")
            if more_buttons:
                more_buttons[0].click()
                time.sleep(1)
                additional_phone_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-6 > span:nth-child(2), div.col-xs-12 > span:nth-child(2)")
                for elem in additional_phone_elements:
                    if phone_number_pattern.match(elem.text):
                        person_info['Phones'].add(elem.text)
        except Exception as e:
            print(f"An error occured {e}. More button wasn't found. Recheck numbers for {person_info.get('Name', 'Unknown')}")


        person_info['Phones'] = list(person_info['Phones'])
        people_data.append(person_info)
        # Check if we are on the last entry and break the loop if so
        viewing_text = driver.find_element(By.CSS_SELECTOR, "div.col-xs-5.text-center").text
        numbers = re.findall(r'\d+', viewing_text)
        current_lead = int(numbers[0])
        if current_lead == total_leads:
            break

        # Move to the next lead
        next_button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='/Lead/MoveNext']")
        next_button.click()
        time.sleep(4)

    return people_data

def save_to_csv(people_data):
    with open('people_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Age', 'City', 'State', 'Phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for person in people_data:
            if person['Phones']:  # If there are phone numbers
                for phone in person['Phones']:
                    writer.writerow({
                        'Name': person['Name'],
                        'Age': person['Age'],
                        'City': person.get('City', 'N/A'),
                        'State': person.get('State', 'N/A'),
                        'Phone': phone
                    })
            else:  # If there are no phone numbers, still write the person's info with 'N/A' for the phone
                writer.writerow({
                    'Name': person['Name'],
                    'Age': person['Age'],
                    'City': person.get('City', 'N/A'),
                    'State': person.get('State', 'N/A'),
                    'Phone': 'N/A'
                })

def main():
    try:
        navigate_and_login(user, password, driver)
        leads_df = scrape_leads(driver)
        save_to_csv(leads_df)
    except Exception as e:
        print(f"An error occured: {e}")
    driver.quit()

if __name__ == "__main__":
    main()

