from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_html_using_search_bar_with_selenium(url_path, input=None, onclick=None):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(url_path)
    if input and onclick:
        for key in list(input.keys()):
            wait.until(EC.visibility_of_element_located((By.XPATH, key))).send_keys(input[key])
        driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, onclick))))
    time.sleep(2)
    content = driver.page_source
    driver.close()
    soup = BeautifulSoup(content, "html.parser")
    return soup
