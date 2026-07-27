"""
Visits the Streamlit app and clicks the wake-up button if the app is asleep.
Runs headless via GitHub Actions on a schedule.
"""
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Replace with your actual live Streamlit app URL
STREAMLIT_URL = "https://your-app-name.streamlit.app"


def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    driver = webdriver.Chrome(options=options)

    try:
        print(f"Visiting {STREAMLIT_URL} ...")
        driver.get(STREAMLIT_URL)

        try:
            wake_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'get this app back up')]")
                )
            )
            print("App is asleep — clicking wake-up button.")
            wake_button.click()

            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(., 'get this app back up')]")
                )
            )
            print("App woke up successfully.")
        except TimeoutException:
            print("No wake-up button found — app is already awake.")

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        driver.quit()
        print("Done.")


if __name__ == "__main__":
    main()
