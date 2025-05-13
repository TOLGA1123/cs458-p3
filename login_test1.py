from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest
    #test case 1 --> valid/invalid login
    
class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #cls.driver = webdriver.Chrome()
        cls.driver = uc.Chrome()        #normal google chrome blocks selenium logins
        cls.driver.get("http://127.0.0.1:3000/")
        cls.driver.maximize_window()
        
    def setUp(self):
        """Ensure a fresh session before each test"""
        self.driver.get("http://127.0.0.1:3000/")
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
        try:
            logout_button = self.driver.find_element(By.ID, "logoutButton")  
            logout_button.click()
            time.sleep(5)
        except:
            pass

    def test_valid_email_login(self):
        """TC001 - Login with a valid email and password"""
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:3000/Home")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")
        driver.get("http://127.0.0.1:5000/session_data")
        session_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("admin@gmail.com", session_text, "Logged-in session user does not match expected email.")

    def test_valid_phone_login(self):
        """TC002 - Login with a valid phone number and password"""
        driver = self.driver
        phone_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        phone_input.clear()
        phone_input.send_keys("+1234567890")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:3000/Home")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")
        driver.get("http://127.0.0.1:5000/session_data")
        session_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("+1234567890", session_text, "Logged-in session user does not match expected phone.")


    def test_invalid_login(self):
        """TC003 - Login with invalid credentials (Should not redirect)"""
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("wronguser@gmail.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        self.assertEqual(driver.current_url, "http://127.0.0.1:3000/")
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid credentials.")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist even after invalid login.")   #session must exist to track # invalid attempts
        

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
