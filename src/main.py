from config import USER, PASSWORD, OUTPUT_CSV
from scraper import create_driver, navigate_and_login, scrape_leads
from utils import setup_logging, save_to_csv, save_invalid_records, save_summary


def main():
    driver = None
    try:
        setup_logging()

        driver = create_driver()
        navigate_and_login(USER, PASSWORD, driver)

        results = scrape_leads(driver)

        save_to_csv(results["records"], OUTPUT_CSV)
        save_invalid_records(results["invalid_records"])
        save_summary(results["summary"])

        print("Run completed successfully.")
        print(results["summary"])

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    main()