import unittest
import time
import imaplib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import email
import os
from dotenv import load_dotenv

load_dotenv()

class WebSurveyEndToEndTest(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService(), options=options)
        self.driver.implicitly_wait(10)

    def test_web_survey_submission(self):
        driver = self.driver
        driver.get("http://127.0.0.1:3000/AI_survey")

        # --- SURVEY PAGE ---
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))

        driver.find_element(By.ID, "name").send_keys("Jane Doe")
        driver.find_element(By.ID, "birth_date").send_keys("05-01-2015")

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
        self.assertTrue(send_btn.is_enabled())
        send_btn.click()

        # --- EMAIL VERIFICATION ---
        email_found = self.wait_for_email(
            recipient="test.hesap458@gmail.com",
            subject_keyword="AI Survey Result",
            timeout=30
        )
        self.assertTrue(email_found, "Survey email was not received within the expected timeframe.")

    def wait_for_email(self, recipient, subject_keyword, timeout=30):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.check_email(recipient, subject_keyword):
                return True
            time.sleep(10)
        return False

    def check_email(self, recipient, subject_keyword):
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"
        password = os.getenv("MAIL_APP_PASSWORD").replace(u'\xa0', u' ')

        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            mail.login(username, password)
            mail.select("inbox")
            result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()

            for mail_id in reversed(mail_ids):
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                date_tuple = email.utils.parsedate_tz(msg["Date"])
                if date_tuple:
                    email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                    now = datetime.now()
                    if now - email_timestamp <= timedelta(minutes=5):
                        print("Email found within last 5 minutes.")
                        mail.logout()
                        return True

            mail.logout()
            return False
        except Exception as e:
            print("Error checking email:", e)
            return False

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
