from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest

    #test case 4 --> multiple failed login attempts session lockout 30 seconds

class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = uc.Chrome()
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

    def test_multiple_failed_logins(self):
        """TC006 - Multiple failed login attempts should lock the session temporarily (30 seconds)"""
        driver = self.driver
        for i in range(3):
            email_input = driver.find_element(By.ID, "user_input")
            password_input = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginButton")
            email_input.clear()
            email_input.send_keys("admin@gmail.com")
            password_input.clear()
            password_input.send_keys("wrongpassword")
            login_button.click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
            error_message = driver.find_element(By.ID, "errorMessage").text
            self.assertEqual(error_message, "Invalid credentials.")
        # After 3 failed attempts, the system should not lock the session yet
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertNotRegex(error_message, r"Too many failed attempts. Please try again in (\d+) seconds.", 
                            "System should not show lock message after 3 failed attempts.")
        # After 4 failed attempts, the system should lock the session for 30 seconds
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        match = re.search(r"Too many failed attempts. Please try again in (\d+) seconds.", error_message)
        self.assertIsNotNone(match, "System should display a lock message with countdown after 4th failed attempt.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:3000/")     #should still be in the login page
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after failed login attempts.")
        time.sleep(30)
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        self.assertEqual(driver.current_url, "http://127.0.0.1:3000/home")



    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
