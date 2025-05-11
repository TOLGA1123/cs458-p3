import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WebSendWithoutModelTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.get("http://localhost:5000/login")  # adjust URL if needed

    def test_send_without_model_selected(self):
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

        # Fill a valid birth date
        birthdate_input = driver.find_element(By.NAME, "birth_date")
        birthdate_input.clear()
        birthdate_input.send_keys("01-01-1990")  # format for <input type="date">

        driver.find_element(By.NAME, "education_level").send_keys("Bachelor's")
        driver.find_element(By.NAME, "city").send_keys("Ankara")

        driver.find_element(By.XPATH, "//input[@name='gender' and @value='Female']").click()

        # Do not select any AI model checkboxes
        # Skip the model selection phase by not interacting with any model checkboxes

        driver.find_element(By.NAME, "use_case").send_keys("It helps me summarize articles.")

        send_btn = driver.find_element(By.ID, "send-btn")

        # Ensure send button is enabled when no models are selected
        self.assertTrue(send_btn.is_enabled(), "Send button should be enabled without any model selected.")
        
        send_btn.click()

        try:
            error = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "model_error"))
            )
            self.assertIn("You must select at least one AI model", error.text)
        except TimeoutException:
            print("Error message not shown.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
