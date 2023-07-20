from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time


def selenium_driver(url, driver_path):
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=driver_path)
    wd = webdriver.Firefox(options=options, service=service)
    wd.get(url)
    time.sleep(2)
    return wd
