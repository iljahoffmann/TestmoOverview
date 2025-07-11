import logging
import time
import os
import glob
import pandas as pd
import requests
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from lib import helper_functions, selenium_driver_functions


def login_to_testmo(driver: WebDriver, xpath_dict: dict, testmo_email, testmo_password):
    """function to login to testmo

    Args:
        driver (str): selenium webdriver
        xpath_dict (dict): xpaths containing the email, password, login elements
    """
    driver.get(xpath_dict["TESTMO_LOGIN_PAGE"]["PATH"])
    email_element = driver.find_element(By.XPATH, xpath_dict["TESTMO_LOGIN_PAGE"]["EMAIL"])
    email_element.send_keys(testmo_email)
    password_element = driver.find_element(By.XPATH, xpath_dict["TESTMO_LOGIN_PAGE"]["PASSWORD"])
    password_element.send_keys(testmo_password)
    login_element = driver.find_element(By.XPATH, xpath_dict["TESTMO_LOGIN_PAGE"]["LOGIN_BUTTON"])
    login_element.click()


def get_all_testmo_projects(testmo_url: str, testmo_api_key: str) -> dict:
    headers = {
        "Authorization": f"Bearer {testmo_api_key}",
        "Content-Type": "application/json",  # Adjust content type if necessary
    }
    response: requests.Response = requests.get(testmo_url + "/api/v1/projects", headers=headers, timeout=30)
    all_projects = response.json()["result"]
    new_dict = []
    for project in all_projects:
        name = project["name"]
        id_ = project["id"]
        new_dict.append({"name": name, "id": id_})
    return new_dict


def read_csv_to_pandas_dataframe(csv_path):
    # reads the csv and returns a pandas dataframe from it
    df = pd.read_csv(csv_path, delimiter=",")
    return df


def download_csv(
        driver: WebDriver,
        project_id: str,
        project_name:str,
        download_path: str,
        xpaths_dict: dict,
        csv_fields,
        overwrite_existing_file=False
) -> str:
    """navigates to the project repo and downloads the repo as csv

    Args:
        driver (str): selenium webdriver
        project_name (str): project_name
        download_path(str): download_path
        xpath_dict (dict): xpaths containing the email, password, login elements
        csv_fields (list): csv_fields as list
        overwrite_existing_file (bool): optional - if True overwrites existing file with the same name

    Returns:
        (str): relative filename of the download in OS format
    """
    project_link = f"https://murrelektronik.testmo.net/repositories/{project_id}"

    driver.get(project_link)
    time.sleep(2)
    
    selenium_driver_functions.click_element(driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT"])
    time.sleep(2)
    
    selenium_driver_functions.click_element(driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_TO_CSV"])
    time.sleep(2)

    selenium_driver_functions.wait_for_element_clickable(
        driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["WINDOW"]
    )
    # Try to deselect the field 'column_selected' (this deselects all fields)
    # if its already deselected, an expcetion is raised an caught"""
    if csv_fields is None:
        pass
    else:
        try:
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column"]
            )
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column"]
            )
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column_selected"]
            )
        except Exception:
            pass
        for field in csv_fields:
            try:
                selenium_driver_functions.scroll_to_element(
                    driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"][str(field)]
                )
            except Exception:
                logging.info(
                    "Couldnt click field %s, "
                    "some custom fields are not present in every testmo repository, this message isnt an issue necessarily",
                    field,
                )
            time.sleep(1)
    # Try to deselect the field 'additional project details'
    # if its already deselected, an expcetion is raised an caught"""
    try:
        selenium_driver_functions.click_element(
            driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["ADDITIONAL_PROJECT_DETAILS_CHECKED"]
        )
    except Exception:
        pass
    selenium_driver_functions.click_element(
        driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["EXPORT_BUTTON"]
    )
    helper_functions.wait_for_download_at_path(download_path)
    list_of_files = glob.glob(download_path+"/*") # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    file_name = "".join(c for c in project_name if c.isalpha() or c.isdigit() or c==' ').rstrip().replace(" ", "")
    relative_filename = os.path.join(download_path, f"{file_name}.csv")
    try:
        if overwrite_existing_file and os.path.exists(relative_filename):
            os.unlink(relative_filename)
        os.rename(latest_file, relative_filename)
    except Exception as ex:
        traceback.print_exception(ex)

    return relative_filename


# <<generator/co-routine>>
def download_fields_and_csv(
        driver: WebDriver,
        project_id: str,
        project_name: str,
        download_path: str,
        xpaths_dict: dict,
        overwrite_existing_file: bool = False,
        testmo_gui_url: str = "https://murrelektronik.testmo.net"
):
    """
    Navigates to the project repo and downloads the repo as csv.

    Args:
        driver (str): selenium webdriver
        project_name (str): project_name
        download_path(str): download_path
        xpath_dict (dict): xpaths containing the email, password, login elements
        overwrite_existing_file (bool): optional - if True overwrites existing file with the same name
        testmo_gui_url (str): optional base URL for testmo GUI - defaults to "https://murrelektronik.testmo.net"

    Inject:
        csv_fields (list): csv_fields as list -- send to first yield

    Yields:
        (str): 1. html of the export table
        (str): 2. relative filename of the download in OS format
    """
    project_link = f"{testmo_gui_url}/repositories/{project_id}"

    driver.get(project_link)
    time.sleep(2)

    selenium_driver_functions.click_element(driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT"])
    time.sleep(2)

    selenium_driver_functions.click_element(driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_TO_CSV"])
    time.sleep(2)

    selenium_driver_functions.wait_for_element_clickable(
        driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["WINDOW"]
    )
    table_html = (driver.find_element(
        By.XPATH, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["TABLE"]
    )
    .get_attribute(
        'outerHTML'
    ))
    csv_fields = yield table_html

    # Try to deselect the field 'column_selected' (this deselects all fields)
    # if its already deselected, an expcetion is raised an caught"""
    if csv_fields is None:
        pass
    else:
        try:
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column"]
            )
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column"]
            )
            selenium_driver_functions.click_element(
                driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["column_selected"]
            )
        except Exception as ex1:
            pass
        for field in csv_fields:
            try:
                xpath = xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"][str(field)]
                selenium_driver_functions.scroll_to_element(driver, xpath)
            except Exception as ex2:
                logging.info(
                    "Couldnt click field %s, "
                    "some custom fields are not present in every testmo repository, this message isnt an issue necessarily",
                    field,
                )
            time.sleep(1)
    # Try to deselect the field 'additional project details'
    # if its already deselected, an expcetion is raised an caught"""
    try:
        selenium_driver_functions.click_element(
            driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["ADDITIONAL_PROJECT_DETAILS_CHECKED"]
        )
    except Exception:
        pass
    selenium_driver_functions.click_element(
        driver, xpaths_dict["TESTMO_REPOSITORY_PAGE"]["EXPORT_CSV_WINDOW"]["EXPORT_BUTTON"]
    )
    helper_functions.wait_for_download_at_path(download_path)
    list_of_files = glob.glob(download_path + "/*")  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    file_name = "".join(c for c in project_name if c.isalpha() or c.isdigit() or c == ' ').rstrip().replace(" ", "")
    relative_filename = os.path.join(download_path, f"{file_name}.csv")
    try:
        if overwrite_existing_file and os.path.exists(relative_filename):
            os.unlink(relative_filename)
        os.rename(latest_file, relative_filename)
    except Exception as ex:
        traceback.print_exception(ex)

    yield relative_filename

