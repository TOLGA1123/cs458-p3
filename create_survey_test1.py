import unittest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class CreateSurveyTest(unittest.TestCase):
    driver: webdriver.Chrome

    @classmethod
    def setUpClass(cls):
        # tell Chrome not to close when the test finishes
        opts = webdriver.ChromeOptions()
        opts.add_experimental_option("detach", True)
        cls.driver = webdriver.Chrome(options=opts)

        cls.driver.get("http://localhost:3000/create-survey")
        cls.driver.maximize_window()

    def find_element(self, by: By, value: str) -> WebElement:
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )

    def test_create_survey_with_options_and_local_storage(self):
        driver = self.driver

        # 1) Fill title & description
        title = self.find_element(By.ID, "survey-title")
        title.clear()
        title.send_keys("My Test Survey")

        desc = self.find_element(By.ID, "survey-description")
        desc.clear()
        desc.send_keys("A test survey with various question types and options.")

        # 2) Add & fill Q1: Multiple Choice
        driver.find_element(By.ID, "add-multiple-choice").click()
        q1 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[1][contains(@class,'relative')]"
        )
        q1.find_element(By.XPATH, ".//input[contains(@id,'-title')]")\
          .send_keys("What is your favorite color?")
        # fill defaults
        mc_defaults = ["Red", "Green", "Blue"]
        opts = q1.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(opts, mc_defaults):
            inp.clear()
            inp.send_keys(text)
        # add a fourth
        q1.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        opts = q1.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        opts[-1].clear()
        opts[-1].send_keys("Purple")

        # 3) Add & fill Q2: Rating
        driver.find_element(By.ID, "add-rating").click()
        q2 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[2][contains(@class,'relative')]"
        )
        q2.find_element(By.XPATH, ".//input[contains(@id,'-title')]")\
           .send_keys("Rate your satisfaction")

        # 4) Add & fill Q3: Text
        driver.find_element(By.ID, "add-text").click()
        q3 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[3][contains(@class,'relative')]"
        )
        q3.find_element(By.XPATH, ".//input[contains(@id,'-title')]")\
           .send_keys("What is your name?")

        # 5) Add & fill Q4: Dropdown
        driver.find_element(By.ID, "add-dropdown").click()
        q4 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[4][contains(@class,'relative')]"
        )
        q4.find_element(By.XPATH, ".//input[contains(@id,'-title')]")\
           .send_keys("Select your country")
        dd_defaults = ["USA", "Canada", "UK"]
        dd_opts = q4.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(dd_opts, dd_defaults):
            inp.clear()
            inp.send_keys(text)
        q4.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        dd_opts = q4.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        dd_opts[-1].clear()
        dd_opts[-1].send_keys("Other")

        # 6) Add & fill Q5: Checkbox
        driver.find_element(By.ID, "add-checkbox").click()
        q5 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[5][contains(@class,'relative')]"
        )
        q5.find_element(By.XPATH, ".//input[contains(@id,'-title')]")\
           .send_keys("Select your interests")
        cb_defaults = ["Sports", "Music", "Travel"]
        cb_opts = q5.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(cb_opts, cb_defaults):
            inp.clear()
            inp.send_keys(text)
        q5.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        cb_opts = q5.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        cb_opts[-1].clear()
        cb_opts[-1].send_keys("Art")

        # 7) Save and accept the alert
        self.find_element(By.ID, "save-button").click()
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()

        # 8) Wait for the app to navigate to /saved-surveys
        WebDriverWait(driver, 10).until(EC.url_contains("/saved-surveys"))

        # 9) Verify localStorage was updated
        stored = driver.execute_script("return window.localStorage.getItem('savedSurveys');")
        self.assertIsNotNone(stored, "No savedSurveys key in localStorage")
        surveys = json.loads(stored)
        self.assertTrue(any(s["title"] == "My Test Survey" for s in surveys),
                        "Saved survey not found in localStorage list")

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        cls.driver.quit()
        pass


if __name__ == "__main__":
    unittest.main()
