import json
import os
import time


def wait_for_download_at_path(download_path: str, timeout=20):
    """waits for a download to finish at download_path
    by waiting for the amount of files at that path
    to inrease by 1

    Args:
        download_path (str): path to download folder
        timeout (int, optional): seconds to wait. Defaults to 15.

    Raises:
        TimeoutError: _description_
    """
    count = len([f for f in os.listdir(download_path) if f.endswith(".csv")])
    start_time = time.time()
    while True:
        new_count = len([f for f in os.listdir(download_path) if f.endswith(".csv")])
        if new_count == count + 1:
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("File download timed out")
        time.sleep(1)


def load_json(json_path: str) -> dict:
    """read json file at json_path

    Args:
        json_path (str): path to json

    Returns:
        dict: dictionary from the json at json_path
    """
    json_data = None
    with open(json_path, encoding="utf-8") as file:
        json_data = json.load(file)
    return json_data


def clear_dir(directory: str):
    """removes files at location

    Args:
        directory (str): dir path
    """
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
