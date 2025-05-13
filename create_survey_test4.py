import unittest, json, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class CreateSurveyTest(unittest.TestCase):
    driver: webdriver.Chrome

    @classmethod
    def setUpClass(cls):
        opts = webdriver.ChromeOptions()
        opts.add_experimental_option("detach", True)     # keep Chrome open
        cls.driver = webdriver.Chrome(options=opts)
        cls.driver.get("http://localhost:3000/create-survey")
        cls.driver.maximize_window()

    # ---------- helpers ----------
    def el(self, by, value) -> WebElement:
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )

    # ---------- test ----------
    def test_no_survey_should_be_saved(self):
        d = self.driver

        # title & description
        self.el(By.ID, "survey-title").clear()
        self.el(By.ID, "survey-title").send_keys("Rapid 10-Q survey")
        self.el(By.ID, "survey-description").clear()
        self.el(By.ID, "survey-description").send_keys("Created by Selenium in one go.")

        # add 10 multiple-choice questions, titles only
        add_btn = self.el(By.ID, "add-multiple-choice")
        for i in range(101):
            add_btn.click()
            card = self.el(
                By.XPATH, f"//div[@class='space-y-4']/div[{i+1}][contains(@class,'relative')]"
            )
            inp = card.find_element(By.XPATH, ".//input[contains(@id,'-title')]")
            inp.clear()
            inp.send_keys(f"Question {i+1}")

        # click Save -> an alert with the error text should appear
        self.el(By.ID, "save-button").click()
        WebDriverWait(d, 5).until(EC.alert_is_present()).accept()

        # manually go (or stay) on /saved-surveys
        d.get("http://localhost:3000/saved-surveys")
        WebDriverWait(d, 10).until(EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        ))

        # 1) check the “No surveys found” empty-state card is visible
        empty_card = self.el(By.XPATH, "//h3[contains(.,'No surveys found')]")
        self.assertTrue(empty_card.is_displayed(), "Empty-state card not shown")

        # 2) confirm localStorage really is empty
        stored = d.execute_script("return window.localStorage.getItem('savedSurveys');")
        self.assertTrue(stored in (None, "", "[]"), "savedSurveys should be empty")

    @classmethod
    def tearDownClass(cls):
        pass   # don’t close Chrome


if __name__ == "__main__":
    unittest.main()
