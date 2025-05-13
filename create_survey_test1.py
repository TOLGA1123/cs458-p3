import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class CreateSurveyTest(unittest.TestCase):
    driver: webdriver.Chrome

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        # Ensure your React app is running on http://localhost:3000 or update the URL
        cls.driver.get("http://localhost:3000/create-survey")
        cls.driver.maximize_window()

    def find_element(self, by: By, value: str) -> WebElement:
        """Helper function to find an element with explicit wait."""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )

    def find_elements(self, by: By, value: str) -> list[WebElement]:
        """Helper function to find elements with explicit wait."""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def test_create_survey_with_all_question_types(self):
        driver = self.driver

        # Wait for survey title input using its existing ID
        self.find_element(By.ID, "survey-title")

        self.find_element(By.ID, "survey-title").click()  # Click the input field to focus it
        self.find_element(By.ID, "survey-title").clear()  # Clear the field
        self.find_element(By.ID, "survey-title").send_keys("My Test Survey")  # Set title programmatically
        
        self.find_element(By.ID, "survey-description").click()  
        self.find_element(By.ID, "survey-description").clear()  
        self.find_element(By.ID, "survey-description").send_keys("A test survey with various question types.")

        self.find_element(By.ID, "add-multiple-choice").click()
        first_question_card = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[1][contains(@class, 'relative')]")

        # Find the first question title input and click to focus, no `send_keys`
        first_question_title_input = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[1]//input[contains(@id, '-title')]")
        first_question_title_input.click()  
        first_question_title_input.clear()  
        first_question_title_input.send_keys("What is your favorite color?")  # Without `send_keys`
        

        self.find_element(By.ID, "add-rating").click()
        second_question_card = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[2][contains(@class, 'relative')]")
        second_question_title_input = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[2]//input[contains(@id, '-title')]")
        second_question_title_input.click()  
        second_question_title_input.clear()  
        second_question_title_input.send_keys("Rate your satisfaction")


        self.find_element(By.ID, "add-text").click()
        third_question_card = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[3][contains(@class, 'relative')]")
        third_question_title_input = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[3]//input[contains(@id, '-title')]")
        third_question_title_input.click()  
        third_question_title_input.clear()  
        third_question_title_input.send_keys("What is your name?")


        self.find_element(By.ID, "add-dropdown").click()
        fourth_question_card = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[4][contains(@class, 'relative')]")
        fourth_question_title_input = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[4]//input[contains(@id, '-title')]")
        fourth_question_title_input.click()  
        fourth_question_title_input.clear()  
        fourth_question_title_input.send_keys("Select your country")


        self.find_element(By.ID, "add-checkbox").click()
        fifth_question_card = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[5][contains(@class, 'relative')]")
        fifth_question_title_input = self.find_element(By.XPATH, "//div[@class='space-y-4']/div[5]//input[contains(@id, '-title')]")
        fifth_question_title_input.click()  
        fifth_question_title_input.clear()  
        fifth_question_title_input.send_keys("Select your interests")

        self.find_element(By.ID, "save-button").click()

        time.sleep(2)
        try:
            # Adjust the XPath or selector based on your UI
            success_alert = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Survey saved successfully')]"))
            )

            # If there is a button to dismiss the alert, click it
            # This could be 'OK', 'Dismiss', or a close (×) button, depending on your UI
            alert_ok_button = self.find_element(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Dismiss') or contains(text(), 'Close') or .//svg[contains(@class, 'close')]]")
            alert_ok_button.click()

        except Exception as e:
            print(f"Success alert not found or could not be closed: {e}")

        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        time.sleep(3)
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()
