from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest

    #test case 5 --> incorrect form inputs (blank, invalid email/phone formats, leading/trailing spaces)
    
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

    def test_blank_fields(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        #Blank email/phone with valid password
        email_input.clear()
        email_input.send_keys("")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Email/Phone field is required.", "Error message for blank email/phone is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        #Valid email/phone and blank password
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Password field is required.", "Error message for blank password is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        #Both fields blank
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("")
        password_input.clear()
        password_input.send_keys("")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Email/Phone and Password are required.", "Error message for both blank fields is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login

    def test_leading_and_trailing_spaces(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("   admin@gmail.com   ")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")      #should redirect to home

    def test_invalid_email_and_phone_format(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin.gmail.com")  #missing '@'
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid email format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("1234")     #invalid phone number
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid phone number format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@@gmail.com")  #extra '@'
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid email format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
