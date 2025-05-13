import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WebBirthdateValidationTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.get("http://127.0.0.1:3000/AI_survey")

    def test_birthdate_in_the_future(self):
        driver = self.driver

        # --- SURVEY PAGE ---
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))

        # --- SURVEY PHASE ---
        driver.find_element(By.ID, "name").send_keys("Jane Doe")

        # Fill a future birth date
        birthdate_input = driver.find_element(By.ID, "birth_date")
        birthdate_input.clear()
        birthdate_input.send_keys("01-01-2030")

        # Handle custom select component robustly
        education_select = driver.find_element(By.ID, "education_level")
        education_select.click()
        time.sleep(0.5)  # Give time for the dropdown to render
        # Find the option container (not just the text node)
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and .=\"Bachelor's Degree\"]"))
        )
        option.click()
        # Wait for the dropdown to close (option disappears)
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@role='option' and .=\"Bachelor's Degree\"]"))
        )
        driver.find_element(By.ID, "city").send_keys("Ankara")

        # Click the label for 'Female' to select the gender
        driver.find_element(By.XPATH, "//label[contains(text(), 'Female')]").click()

        # Select models "ChatGPT" and "Bard"
        desired_models = ["ChatGPT", "Bard"]
        model_pairs = driver.find_elements(By.CSS_SELECTOR, ".model-pair")

        for pair in model_pairs:
            label = pair.find_element(By.CSS_SELECTOR, "label.option")
            label_text = label.text.strip()

            if label_text in desired_models:
                checkbox = pair.find_element(By.CSS_SELECTOR, '[role="checkbox"]')
                checkbox.click()

                # Safer and clearer way to get the associated cons input
                cons_input = pair.find_element(By.CSS_SELECTOR, ".cons-field")
                cons_input.clear()
                cons_input.send_keys("None")

        driver.find_element(By.ID, "use_case").send_keys("It helps me summarize articles.")
        
        send_btn = driver.find_element(By.ID, "send-btn")
        self.assertFalse(send_btn.is_enabled(), "Send button should be disabled with future birthdate.")

        try:
            error = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "birthdate_error"))
            )
            self.assertIn("Birth date cannot be in the future", error.text.replace(u'\xa0', u' '))
        except TimeoutException:
            print("Error message not shown.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
