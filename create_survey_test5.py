import unittest, json, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://localhost:3000"

class ValidationFlowTest(unittest.TestCase):
    driver: webdriver.Chrome

    @classmethod
    def setUpClass(cls):
        opts = webdriver.ChromeOptions()
        opts.add_experimental_option("detach", True)   # keep browser open if you like
        cls.driver = webdriver.Chrome(options=opts)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 8)

    # ---------- small helpers -------------------------------------------------
    def goto(self, url: str):
        self.driver.get(url)

    def wait_alert_and_accept(self):
        self.wait.until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        time.sleep(0.3)           # tiny pause for React-router

    def is_saved_survey_present(self, title: str) -> bool:
        stored = self.driver.execute_script("return window.localStorage.getItem('savedSurveys')")
        if not stored:
            return False
        try:
            return any(s["title"] == title for s in json.loads(stored))
        except Exception:
            return False

    def assert_no_surveys_page(self):
        self.goto(f"{BASE}/saved-surveys")
        # the empty-state card has this text:
        empty_text = "No surveys found"
        self.assertTrue(
            empty_text in self.driver.page_source,
            f"Expected '{empty_text}' on saved-surveys page",
        )

    # ---------- the actual test ----------------------------------------------
    def test_all_invalid_save_paths(self):
        TITLE  = "Should-Not-Exist"
        DESC   = "Temp description"
        DRIVER = self.driver

        # ── 1. title+desc but NO QUESTIONS ────────────────────────────────────
        self.goto(f"{BASE}/create-survey")
        DRIVER.find_element(By.ID, "survey-title").clear()
        DRIVER.find_element(By.ID, "survey-title").send_keys(TITLE)
        DRIVER.find_element(By.ID, "survey-description").clear()
        DRIVER.find_element(By.ID, "survey-description").send_keys(DESC)

        DRIVER.find_element(By.ID, "save-button").click()
        self.wait_alert_and_accept()

        # verify nothing saved
        self.assertFalse(self.is_saved_survey_present(TITLE))
        self.assert_no_surveys_page()

        # ── 2. NO TITLE, at least one question ────────────────────────────────
        self.goto(f"{BASE}/create-survey")
        # leave title blank
        DRIVER.find_element(By.ID, "survey-description").send_keys(DESC)
        DRIVER.find_element(By.ID, "add-multiple-choice").click()

        DRIVER.find_element(By.ID, "save-button").click()
        self.wait_alert_and_accept()

        self.assertFalse(self.is_saved_survey_present(TITLE))
        self.assert_no_surveys_page()

        # ── 3. TITLE but NO DESCRIPTION, one question ─────────────────────────
        self.goto(f"{BASE}/create-survey")
        DRIVER.find_element(By.ID, "survey-title").send_keys(TITLE)
        # leave description blank
        DRIVER.find_element(By.ID, "add-multiple-choice").click()

        DRIVER.find_element(By.ID, "save-button").click()
        self.wait_alert_and_accept()

        self.assertFalse(self.is_saved_survey_present(TITLE))
        self.assert_no_surveys_page()
    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        # keep the window open; comment out if you prefer auto-close
        pass
        # cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
