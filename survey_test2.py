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
        self.driver.get("http://localhost:5000/login")  # adjust URL if needed

    def test_birthdate_in_the_future(self):
        driver = self.driver

        # --- LOGIN PHASE ---
        email_field = driver.find_element(By.NAME, "user_input")
        email_field.send_keys("admin@gmail.com")

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("password123")

        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Go to Survey")))
        driver.find_element(By.LINK_TEXT, "Go to Survey").click()

        # --- SURVEY PAGE ---
        WebDriverWait(driver, 10).until(EC.url_contains("/survey"))

        # --- SURVEY PHASE ---
        driver.find_element(By.NAME, "name").send_keys("Jane Doe")

        # Fill a future birth date manually (adjust format as per input type)
        birthdate_input = driver.find_element(By.NAME, "birth_date")
        birthdate_input.clear()
        birthdate_input.send_keys("01-01-2030")  # format for <input type="date">

        driver.find_element(By.NAME, "education_level").send_keys("Bachelor's")
        driver.find_element(By.NAME, "city").send_keys("Ankara")

        driver.find_element(By.XPATH, "//input[@name='gender' and @value='Female']").click()

        # Select models "ChatGPT" and "Bard"
        desired_models = ["ChatGPT", "Bard"]
        model_pairs = driver.find_elements(By.CSS_SELECTOR, ".model-pair")

        for pair in model_pairs:
            label = pair.find_element(By.CSS_SELECTOR, "label.option")
            label_text = label.text.strip()

            if label_text in desired_models:
                checkbox = label.find_element(By.TAG_NAME, "input")
                if not checkbox.is_selected():
                    checkbox.click()

                # Safer and clearer way to get the associated cons input
                cons_input = pair.find_element(By.CSS_SELECTOR, ".cons-field")
                cons_input.clear()
                cons_input.send_keys("None")

        driver.find_element(By.ID, "use_case").send_keys("It helps me summarize articles.")
        
        send_btn = driver.find_element(By.ID, "send-btn")
        self.assertFalse(send_btn.is_enabled())
        send_btn.click()

        send_button = driver.find_element(By.ID, "send-btn")
        self.assertFalse(send_button.is_enabled(), "Send button should be disabled with future birthdate.")

        try:
            error = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "birthdate_error"))
            )
            self.assertIn("Birthdate cannot be in the future", error.text)
        except TimeoutException:
            print("Error message not shown.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
