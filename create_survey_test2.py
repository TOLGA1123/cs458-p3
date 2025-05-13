import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:3000"

@pytest.fixture
def driver():
    # you can swap Chrome() for Firefox(), etc.
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def test_conditional_question_shows_in_preview(driver):
    wait = WebDriverWait(driver, 10)
    driver.get(f"{BASE_URL}/create-survey")

    # 1) Add Q1: Multiple Choice
    btn_mc = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Multiple Choice')]")
    ))
    btn_mc.click()

    # 2) Fill Q1 title
    #    We look for the first text input under the question-list container.
    q1_input = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[placeholder="Enter question text"]')
    ))
    q1_input.clear()
    q1_input.send_keys("Do you like cats?")

    # 3) Add Q2: Multiple Choice
    btn_mc.click()

    # 4) Fill Q2 title (the second such input)
    all_q_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder="Enter question text"]')
    assert len(all_q_inputs) >= 2, "Two question inputs expected"
    q2_input = all_q_inputs[1]
    q2_input.clear()
    q2_input.send_keys("Why cats?")

    # 5) Enable conditional logic on Q2
    #    The shadcn Switch renders as a button[role="switch"]
    switches = driver.find_elements(By.CSS_SELECTOR, 'button[role="switch"]')
    assert len(switches) >= 2, "At least two switches (one per question)"
    switches[1].click()

    # 6) Pick Parent Question = "Do you like cats?"
    #    Open the parent-select
    parent_triggers = driver.find_elements(By.CSS_SELECTOR, 'button[id$="-parent"]')
    assert len(parent_triggers) >= 2
    parent_triggers[1].click()
    #    Choose that option from the dropdown list
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//li[contains(., 'Do you like cats?')]")
    )).click()

    # 7) Pick Parent Answer = "Option 1"
    answer_triggers = driver.find_elements(By.CSS_SELECTOR, 'button[id$="-answer"]')
    assert len(answer_triggers) >= 2
    answer_triggers[1].click()
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//li[contains(., 'Option 1')]")
    )).click()

    # 8) Switch to Preview tab
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(.,'Preview Survey')]")
    )).click()

    # 9) Select "Option 1" under Q1 in preview
    #    The preview radio has name="preview-<question.id>" and value="Option 1"
    opt1_radio = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'input[type="radio"][value="Option 1"]')
    ))
    opt1_radio.click()

    # 10) Assert that Q2 ("Why cats?") is now visible
    q2_heading = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//h3[contains(text(), 'Why cats?')]")
    ))
    assert q2_heading.is_displayed(), "Conditional question did not appear in preview"

    # Give a moment to see the result if running interactively
    time.sleep(1)
