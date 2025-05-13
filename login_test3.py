from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest

    #test case 3 --> check multiple user log in behavior on different browsers or incognito mode

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

    def test_two_parallel_logins(self):
        """Test logging in with two different accounts in the same test""" #one chrome + one incognito
        driver1 = webdriver.Chrome()
        driver1.get("http://127.0.0.1:3000/")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        driver2 = webdriver.Chrome(options=chrome_options)
        driver2.get("http://127.0.0.1:3000/")
        email1 = driver1.find_element(By.ID, "user_input")
        password1 = driver1.find_element(By.ID, "password")
        login_button1 = driver1.find_element(By.ID, "loginButton")
        email1.send_keys("admin@gmail.com")
        password1.send_keys("password123")
        login_button1.click()
        WebDriverWait(driver1, 32).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        print("First user logged in:", driver1.current_url)
        email2 = driver2.find_element(By.ID, "user_input")
        password2 = driver2.find_element(By.ID, "password")
        login_button2 = driver2.find_element(By.ID, "loginButton")
        email2.send_keys("admin2@gmail.com")
        password2.send_keys("password123")
        login_button2.click()
        WebDriverWait(driver2, 32).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        print("Second user logged in:", driver2.current_url)
        cookies1 = driver1.get_cookies()
        cookies2 = driver2.get_cookies()
        session_cookie1 = next((cookie for cookie in cookies1 if cookie['name'] == 'session'), None)
        session_cookie2 = next((cookie for cookie in cookies2 if cookie['name'] == 'session'), None)
        assert session_cookie1 is not None, "Session cookie should exist for first user."
        assert session_cookie2 is not None, "Session cookie should exist for second user."
        assert session_cookie1 != session_cookie2, "Sessions should be different for each user."
        driver1.get("http://127.0.0.1:5000/session_data")
        session_text = driver1.find_element(By.TAG_NAME, "body").text
        self.assertIn("admin@gmail.com", session_text, "Logged-in session user 1 does not match expected email.")
        driver2.get("http://127.0.0.1:5000/session_data")
        session_text = driver2.find_element(By.TAG_NAME, "body").text
        self.assertIn("admin2@gmail.com", session_text, "Logged-in session user 2 does not match expected email.")
        driver1.quit()
        driver2.quit()

    def test_parallel_logins_chrome_firefox(self):
        """Test logging in with two different accounts in Chrome and Firefox"""
        driver1 = webdriver.Chrome()
        driver1.get("http://127.0.0.1:3000/")
        driver2 = webdriver.Firefox()
        driver2.get("http://127.0.0.1:3000/")
        email1 = driver1.find_element(By.ID, "user_input")
        password1 = driver1.find_element(By.ID, "password")
        login_button1 = driver1.find_element(By.ID, "loginButton")
        email1.send_keys("admin@gmail.com")
        password1.send_keys("password123")
        login_button1.click()
        WebDriverWait(driver1, 32).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        print("First user logged in (Chrome):", driver1.current_url)
        email2 = driver2.find_element(By.ID, "user_input")
        password2 = driver2.find_element(By.ID, "password")
        login_button2 = driver2.find_element(By.ID, "loginButton")
        email2.send_keys("admin2@gmail.com")
        password2.send_keys("password123")
        login_button2.click()
        WebDriverWait(driver2, 32).until(EC.url_contains("http://127.0.0.1:3000/Home"))
        print("Second user logged in (Firefox):", driver2.current_url)
        cookies1 = driver1.get_cookies()
        cookies2 = driver2.get_cookies()
        session_cookie1 = next((cookie for cookie in cookies1 if cookie['name'] == 'session'), None)
        session_cookie2 = next((cookie for cookie in cookies2 if cookie['name'] == 'session'), None)
        assert session_cookie1 is not None, "Session cookie should exist for first user."
        assert session_cookie2 is not None, "Session cookie should exist for second user."
        assert session_cookie1 != session_cookie2, "Sessions should be different for each user."
        driver1.get("http://127.0.0.1:5000/session_data")
        session_text1 = driver1.find_element(By.TAG_NAME, "body").text
        assert "admin@gmail.com" in session_text1, "Logged-in session user 1 does not match expected email."
        driver2.get("http://127.0.0.1:5000/session_data")
        session_text2 = driver2.find_element(By.TAG_NAME, "body").text
        assert "admin2@gmail.com" in session_text2, "Logged-in session user 2 does not match expected email."
        driver1.quit()
        driver2.quit()



    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
