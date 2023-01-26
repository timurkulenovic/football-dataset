from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def selenium_driver(url, driver_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    wd = webdriver.Chrome(driver_path)
    wd.get(url)
    time.sleep(2)
    return wd
