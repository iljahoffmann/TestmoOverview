import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service


def setup_driver(download_path: str, headless: bool = True) -> WebDriver:
    """Function to create and return a selenium driver (chrome)

    Args:
        download_path (file_path): path to download folder
        headless (bool): hide browser - defaults to True

    Returns:
        _type_: selenium driver
    """
    os.path.exists(download_path)
    # the path wasnt being accepted without first calling os.path.join on it
    fixed_path = os.path.join(download_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("ignore-certificate-errors")
    options.add_argument("--lang=en-EN")
    options.add_argument("window-size=1920,1080")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")  # Suppress most Chrome logs
    options.add_argument("--disable-logging")  # Suppress additional logging

    prefs = {"download.default_directory": fixed_path}
    options.add_experimental_option("prefs", prefs)
    options.browser_version = "stable"

    # Select appropriate null device for your OS
    null_device = 'NUL' if os.name == 'nt' else '/dev/null'

    # Use Service to suppress chromedriver logs
    service = Service(log_output=null_device)

    driver = webdriver.Chrome(options=options, service=service)
    driver.implicitly_wait(5)
    return driver


def wait_for_element_clickable(driver: WebDriver, xpath, timeout=10):
    """wait for an html element to be clickable

    Args:
        driver (_type_): selenium driver
        xpath (_type_): xpath to element
        timeout (int, optional): amount of seconds to wait. Defaults to 5.
    """
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def click_element(driver: WebDriver, xpath, timeout=5):
    """clicks the element in the driver at xpath

    Args:
        driver (_type_): selenium driver
        xpath (_type_): xpath to element
        timeout (int, optional): amount of seconds to wait. Defaults to 5.
    """
    wait_for_element_clickable(driver, xpath, timeout)
    web_element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", web_element)


def scroll_to_element(driver: WebDriver, xpath: str):
    """scrolls to html element and clicks it

    Args:
        driver (webdriver): selenium webdriver
        xpath (str): xpath
    """
    web_element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].scrollIntoView();", web_element)
    web_element.click()
