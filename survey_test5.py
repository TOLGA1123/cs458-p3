import unittest
import time
import imaplib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import email
import os
from dotenv import load_dotenv

load_dotenv()

class SendDifferentWebForm(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService(), options=options)
        self.driver.implicitly_wait(10)

    def test_web_submission_multiple_forms(self):
        driver = self.driver
        driver.get("http://localhost:5000/login")

        # --- LOGIN PHASE ---
        driver.find_element(By.ID, "user_input").send_keys("admin@gmail.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "loginButton").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Go to Survey"))).click()

        WebDriverWait(driver, 10).until(EC.url_contains("/survey"))

        # First Submission (Test1)
        self.fill_survey_form("Test1", "Helps me summarize articles.")
        send_button = driver.find_element(By.ID, "send-btn")
        self.assertTrue(send_button.is_enabled())
        send_button.click()

        # Attempt to send same form again
        for i in range(3):
            send_button.click()
            print(f"Send button clicked {i+1} times")
            time.sleep(1)

        error_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "multiple_send_error"))
        )
        self.assertIn("You can only submit same form contents once.", error_element.text)

        # Modify form and submit again (Test2)
        name_input = driver.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("Test2")

        use_case = driver.find_element(By.ID, "use_case")
        use_case.clear()
        use_case.send_keys("I Hate AI")

        send_button = driver.find_element(By.ID, "send-btn")
        self.assertTrue(send_button.is_enabled())
        send_button.click()

        # --- EMAIL VERIFICATION ---
        email_found = self.wait_for_email("test.hesap458@gmail.com", "AI Survey Result", timeout=30)
        self.assertTrue(email_found, "Survey emails not found for both Test1 and Test2")

    def fill_survey_form(self, name, use_case_text):
        driver = self.driver
        driver.find_element(By.ID, "name").clear()
        driver.find_element(By.ID, "name").send_keys(name)

        driver.find_element(By.ID, "birth_date").clear()
        driver.find_element(By.ID, "birth_date").send_keys("01-05-2015")

        Select(driver.find_element(By.ID, "education_level")).select_by_visible_text("Bachelor's")
        driver.find_element(By.ID, "city").clear()
        driver.find_element(By.ID, "city").send_keys("Ankara")

        driver.find_element(By.XPATH, "//input[@name='gender' and @value='Female']").click()

        desired_models = ["ChatGPT", "Bard"]
        model_pairs = driver.find_elements(By.CSS_SELECTOR, ".model-pair")

        for pair in model_pairs:
            label = pair.find_element(By.CSS_SELECTOR, "label.option")
            label_text = label.text.strip()  # This should work fine if the model names are clean

            if label_text in desired_models:
                checkbox = label.find_element(By.TAG_NAME, "input")
                if not checkbox.is_selected():
                    checkbox.click()

                # Find and clear cons input, then enter new value
                cons_input = pair.find_element(By.CSS_SELECTOR, ".cons-field")
                cons_input.clear()
                cons_input.send_keys("None")

        driver.find_element(By.ID, "use_case").clear()
        driver.find_element(By.ID, "use_case").send_keys(use_case_text)

    def wait_for_email(self, recipient, subject_keyword, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            names_found = self.check_email(recipient, subject_keyword)
            if "Test1" in names_found and "Test2" in names_found:
                return True
            time.sleep(10)
        return False

    def check_email(self, recipient, subject_keyword):
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"
        password = os.getenv("MAIL_APP_PASSWORD")
        found_names = set()
        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select("inbox")
            _, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()

            for mail_id in reversed(mail_ids):
                _, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                date_tuple = email.utils.parsedate_tz(msg["Date"])
                email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

                if datetime.now() - email_timestamp > timedelta(minutes=5):
                    continue

                body = self.extract_body_from_email(msg)
                if "Name: Test1" in body:
                    found_names.add("Test1")
                if "Name: Test2" in body:
                    found_names.add("Test2")

                if found_names == {"Test1", "Test2"}:
                    break

            mail.logout()
        except Exception as e:
            print("Error checking email:", e)
        return found_names

    def extract_body_from_email(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()
        return ""

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
