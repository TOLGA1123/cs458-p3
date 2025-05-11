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

class WebSurveyDuplicateSendTest(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService(), options=options)
        self.driver.implicitly_wait(10)

    def test_multiple_sends_same_content(self):
        driver = self.driver
        driver.get("http://localhost:5000/login")

        # --- LOGIN ---
        driver.find_element(By.ID, "user_input").send_keys("admin@gmail.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "loginButton").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Go to Survey")))

        # Navigate to survey page
        driver.find_element(By.LINK_TEXT, "Go to Survey").click()

        # --- FILL FORM ---
        WebDriverWait(driver, 10).until(EC.url_contains("/survey"))

        driver.find_element(By.ID, "name").send_keys("Jane Doe")
        driver.find_element(By.ID, "birth_date").send_keys("01-05-2015")

        Select(driver.find_element(By.ID, "education_level")).select_by_visible_text("Bachelor's")
        driver.find_element(By.ID, "city").send_keys("Ankara")

        driver.find_element(By.XPATH, "//input[@name='gender' and @value='Female']").click()

        # Select ChatGPT model
        model_pairs = driver.find_elements(By.CSS_SELECTOR, ".model-pair")
        for pair in model_pairs:
            label = pair.find_element(By.CSS_SELECTOR, "label.option")
            if label.text.strip() == "ChatGPT":
                checkbox = label.find_element(By.TAG_NAME, "input")
                if not checkbox.is_selected():
                    checkbox.click()
                cons_input = pair.find_element(By.CSS_SELECTOR, ".cons-field")
                cons_input.clear()
                cons_input.send_keys("None")

        driver.find_element(By.ID, "use_case").send_keys("Helps me summarize articles.")

        send_btn = driver.find_element(By.ID, "send-btn")
        self.assertTrue(send_btn.is_enabled())

        # --- MULTIPLE SEND CLICKS ---
        for i in range(3):
            send_btn.click()
            print(f"Send clicked {i + 1} times")
            time.sleep(1)  # brief pause

        # --- EXPECT ERROR MESSAGE ---
        multiple_send_error = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "multiple_send_error"))
        )
        self.assertIn("You can only submit same form contents once.", multiple_send_error.text)

         # --- EMAIL VERIFICATION VIA IMAP ---
        email_found = self.wait_for_email(
            recipient="test.hesap458@gmail.com",
            subject_keyword="AI Survey Result",
            timeout=30
        )
        self.assertTrue(email_found, "Survey email was not received within the expected timeframe.")

    def wait_for_email(self, recipient, subject_keyword, timeout=30):
        start_time = time.time()
        first_email_timestamp = None
        first_email_body = None
        while (time.time() - start_time) < timeout:
            email_found, multiple_emails = self.check_email(
                recipient, subject_keyword, first_email_timestamp, first_email_body
            )
            if email_found:
                if multiple_emails:
                    print("Multiple emails found with the same body content within the last 30 seconds.")
                    return False  # Fail if multiple found
                return True
            time.sleep(10)
        return False

    def check_email(self, recipient, subject_keyword, first_email_timestamp, first_email_body):
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"
        password = os.getenv("MAIL_APP_PASSWORD")
        multiple_emails = False

        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            mail.login(username, password)
            mail.select("inbox")
            result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()

            email_count = 0

            for mail_id in reversed(mail_ids):
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                date_tuple = email.utils.parsedate_tz(msg["Date"])

                email_body = self.extract_body_from_email(msg)

                if email_body:
                    # If it's the first email, save the timestamp and body content
                    if not first_email_timestamp:
                        first_email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        first_email_body = email_body
                        email_count += 1

                    # If the email body is the same as the first email and within 30 seconds, flag it as multiple
                    elif email_body == first_email_body:
                        email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        if datetime.now() - email_timestamp <= timedelta(seconds=30):
                            multiple_emails = True
                            break

            mail.logout()
            return email_count > 0, multiple_emails  # Return whether any email was found and if multiple were found
        except Exception as e:
            print("Error checking email:", e)
            return False, False

    def extract_body_from_email(self, msg):
        """Extracts the body content from the email."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    return body
        else:
            return msg.get_payload(decode=True).decode()

        return None

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
