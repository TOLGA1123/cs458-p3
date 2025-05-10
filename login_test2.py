from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest

    #test case 2 --> valid/invalid google login

class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #cls.driver = webdriver.Chrome()
        cls.driver = uc.Chrome()        #normal google chrome blocks selenium logins
        cls.driver.get("http://127.0.0.1:5000/login")
        cls.driver.maximize_window()
        
    def setUp(self):
        """Ensure a fresh session before each test"""
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
        try:
            logout_button = self.driver.find_element(By.ID, "logoutButton")  
            logout_button.click()
            time.sleep(5)
        except:
            pass

    def test_valid_google_login(self):
        """TC004 - Test Google Login"""
        driver = self.driver
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "identifier")))
        email_input.send_keys("test.hesap458@gmail.com")
        email_input.send_keys(Keys.RETURN)
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        driver.execute_script("arguments[0].click();", next_button)

        time.sleep(3)       #fix
        password_input = WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))  #visibility instead of located
        password_input.send_keys("CS458TestHesap")
        
        password_next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "passwordNext")))
        driver.execute_script("arguments[0].click();", password_next_button)
        continue_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button/span[contains(text(), 'Continue')]")))
        driver.execute_script("arguments[0].click();", continue_button)
        WebDriverWait(driver, 30).until(EC.url_to_be("http://127.0.0.1:5000/"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")
        driver.get("http://127.0.0.1:5000/session_data")
        session_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("test.hesap458@gmail.com", session_text, "Logged-in session user does not match expected email.")

    def test_invalid_google_login(self):
        """TC005 - Test Google Login with Invalid Credentials"""
        driver = self.driver
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "identifier")))
        email_input.send_keys("invalidemail333@gmail.com")
        email_input.send_keys(Keys.RETURN)
        error_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Couldn’t find your Google Account')]")))
        self.assertIsNotNone(error_message, "Error message should be displayed for invalid email")
        driver.get("http://127.0.0.1:5000/login")
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "identifier")))
        email_input.clear()
        email_input.send_keys("test.hesap458@gmail.com")
        email_input.send_keys(Keys.RETURN)
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        driver.execute_script("arguments[0].click();", next_button)

        time.sleep(3)           #fix
        password_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
        password_input.send_keys("WrongPassword123")

        
        password_next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "passwordNext")))
        driver.execute_script("arguments[0].click();", password_next_button)
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        self.assertTrue("accounts.google.com" in driver.current_url, "Should remain on Google login page after failed attempt")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNone(session_cookie, "Session cookie should NOT exist after failed login")

    


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
