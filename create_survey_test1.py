import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class SurveyCreationTest(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService(), options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def test_create_full_survey(self):
        driver = self.driver
        wait = self.wait
        driver.get("http://localhost:5000/create-survey")

        # Set survey title
        driver.find_element(By.ID, "survey_title").send_keys("Full Test Survey")

        # Add Multiple Choice
        self.add_question("Which fruits do you like?", "multiple", options=["Apple", "Banana", "Cherry"])

        # Add Rating
        self.add_question("Rate your satisfaction with our app", "rating", min_rating=1, max_rating=10)

        # Add Open Text
        self.add_question("Any feedback or suggestions?", "text")

        # Add Dropdown
        self.add_question("How often do you use the app?", "dropdown", options=["Daily", "Weekly", "Never"])

        # Add Conditional Text Question (Shown only if "Never" selected)
        self.add_question(
            "Why don't you use the app regularly?", "text", conditional={"question_index": 3, "value": "Never"}
        )

        # Submit the survey
        driver.find_element(By.XPATH, "//button[contains(text(), 'Save Survey')]").click()

        # Wait for redirect
        time.sleep(2)
        self.assertIn("/survey/", driver.current_url)

    def add_question(self, text, qtype, options=None, min_rating=None, max_rating=None, conditional=None):
        driver = self.driver
        wait = self.wait

        # Click add question
        driver.find_element(By.XPATH, "//button[contains(text(), 'Add Question')]").click()
        time.sleep(1)  # wait for question block to appear

        # Get last question block
        question_blocks = driver.find_elements(By.CLASS_NAME, "question-block")
        block = question_blocks[-1]

        # Fill question text
        block.find_element(By.NAME, "question_text").send_keys(text)

        # Select question type
        Select(block.find_element(By.NAME, "question_type")).select_by_value(qtype)
        time.sleep(0.5)

        # Add options for select types
        if qtype in ["multiple", "checkbox", "dropdown"]:
            add_option_btn = block.find_element(By.XPATH, ".//button[contains(text(), 'Add Option')]")
            for i, option in enumerate(options):
                if i > 0:  # First option already exists
                    add_option_btn.click()
                    time.sleep(0.2)
            inputs = block.find_elements(By.NAME, "option_item")
            for input_el, val in zip(inputs, options):
                input_el.send_keys(val)

        elif qtype == "rating":
            block.find_element(By.NAME, "min_rating").clear()
            block.find_element(By.NAME, "min_rating").send_keys(str(min_rating))
            block.find_element(By.NAME, "max_rating").clear()
            block.find_element(By.NAME, "max_rating").send_keys(str(max_rating))

        # Conditional logic
        if conditional:
            logic_q = Select(block.find_element(By.CLASS_NAME, "logic-question"))
            logic_q.select_by_value(str(conditional["question_index"]))
            block.find_element(By.CLASS_NAME, "logic-value").send_keys(conditional["value"])

        time.sleep(0.5)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
