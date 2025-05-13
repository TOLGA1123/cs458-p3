import json
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class SurveyCreationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.get("http://localhost:3000/create-survey")
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)

    def test_survey_auto_persistence_on_reload(self):
        driver = self.driver

        # 1) Fill title & description
        title = self.find_element(By.ID, "survey-title")
        title.clear()  # Clear any pre-existing text
        title.send_keys("My Test Survey")

        desc = self.find_element(By.ID, "survey-description")
        desc.clear()  # Clear any pre-existing text
        desc.send_keys("A test survey with various question types and options.")

        # 2) Add & fill Q1: Multiple Choice
        driver.find_element(By.ID, "add-multiple-choice").click()
        q1 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[1][contains(@class,'relative')]"
        )
        q1_title = q1.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
        q1_title.clear()  # Clear any pre-existing text
        q1_title.send_keys("What is your favorite color?")

        mc_defaults = ["Red", "Green", "Blue"]
        opts = q1.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(opts, mc_defaults):
            inp.clear()  # Clear any pre-existing option text
            inp.send_keys(text)
        q1.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        opts = q1.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        opts[-1].clear()  # Clear the last option before adding new text
        opts[-1].send_keys("Purple")

        # 3) Add & fill Q2: Rating
        driver.find_element(By.ID, "add-rating").click()
        q2 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[2][contains(@class,'relative')]"
        )
        q2_title = q2.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
        q2_title.clear()  # Clear any pre-existing text
        q2_title.send_keys("Rate your satisfaction")

        # 4) Add & fill Q3: Text
        driver.find_element(By.ID, "add-text").click()
        q3 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[3][contains(@class,'relative')]"
        )
        q3_title = q3.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
        q3_title.clear()  # Clear any pre-existing text
        q3_title.send_keys("What is your name?")

        # 5) Add & fill Q4: Dropdown
        driver.find_element(By.ID, "add-dropdown").click()
        q4 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[4][contains(@class,'relative')]"
        )
        q4_title = q4.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
        q4_title.clear()  # Clear any pre-existing text
        q4_title.send_keys("Select your country")
        dd_defaults = ["USA", "Canada", "UK"]
        dd_opts = q4.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(dd_opts, dd_defaults):
            inp.clear()  # Clear any pre-existing option text
            inp.send_keys(text)
        q4.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        dd_opts = q4.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        dd_opts[-1].clear()  # Clear the last option before adding new text
        dd_opts[-1].send_keys("Other")

        # 6) Add & fill Q5: Checkbox
        driver.find_element(By.ID, "add-checkbox").click()
        q5 = self.find_element(By.XPATH,
            "//div[@class='space-y-4']/div[5][contains(@class,'relative')]"
        )
        q5_title = q5.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
        q5_title.clear()  # Clear any pre-existing text
        q5_title.send_keys("Select your interests")
        cb_defaults = ["Sports", "Music", "Travel"]
        cb_opts = q5.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        for inp, text in zip(cb_opts, cb_defaults):
            inp.clear()  # Clear any pre-existing option text
            inp.send_keys(text)
        q5.find_element(By.XPATH, ".//button[contains(., 'Add Option')]").click()
        time.sleep(0.5)
        cb_opts = q5.find_elements(By.XPATH, ".//input[contains(@placeholder,'Option')]")
        cb_opts[-1].clear()  # Clear the last option before adding new text
        cb_opts[-1].send_keys("Art")

        # 7) Save the survey
        driver.find_element(By.ID, "save-button").click()  # Assuming there's a save button
        time.sleep(1)
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "create-new-survey"))
        )
        button.click()

        # 1) Fill title & description
        title = self.find_element(By.ID, "survey-title")
        title.clear()  # Clear any pre-existing text
        title.send_keys("My Test Survey")

        desc = self.find_element(By.ID, "survey-description")
        desc.clear()  # Clear any pre-existing text
        desc.send_keys("A test survey with various question types and options.")

        # 7) Save the survey
        driver.find_element(By.ID, "save-button").click()  # Assuming there's a save button
        time.sleep(1)
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        surveys_container = self.wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "grid"))
        )

        # Find all survey cards in the container. Assuming they are wrapped in "Card" elements.
        surveys_list = surveys_container.find_elements(By.CLASS_NAME, "relative")  # You might need to update this class

        # Verify that the number of surveys matches the expected count (e.g., 2).
        self.assertEqual(len(surveys_list), 2)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
