from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from free_space import free_space
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import argparse

from time import sleep

LOGIN_PAGE = "https://scientia-rb-rhul.azurewebsites.net/app/booking-types"
AVAILABILITY_URL = "https://scientia-eu-v3-2-2-api-d2-02.azurewebsites.net/api/Resources/{{roomId}}/BookingRequests?StartDate=2022-01-31T00:00:00.000Z&EndDate=2022-02-10T23:59:00.000Z&CheckSplitPermissions=false"
MAX_WAIT = 15


def main():
    args = get_login_details()
    chromedriver_autoinstaller.install()

    browser = webdriver.Chrome()

    login(browser, args)
    data = get_room_ids(browser)
    browser.close()
    print(get_availability(data, datetime(2022, 2, 7), datetime(2022, 2, 11)))


def get_login_details():
    parser = argparse.ArgumentParser(description="Mark attendance for RHUL")
    parser.add_argument(
        "-u", "--username", help="Full username for RHUL", required=True
    )
    parser.add_argument("-p", "--password",
                        help="Password for RHUL", required=True)

    return vars(parser.parse_args())


def login(browser, args):
    # Navigate to Login page
    browser.get(LOGIN_PAGE)

    # Wait for button to load
    button = WebDriverWait(browser, MAX_WAIT).until(
        EC.presence_of_element_located((By.ID, "ember529")))
    button.click()
    # Login
    browser.find_element(By.ID, "userNameInput").send_keys(args["username"])
    browser.find_element(By.ID, "passwordInput").send_keys(args["password"])

    browser.find_element(By.ID, "submitButton").click()

    return browser.current_url == LOGIN_PAGE


def get_room_ids(browser):
    token = ""
    room_list = []
    # Nav to "Book a Study room" page once loaded
    link = WebDriverWait(browser, MAX_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "resourcesGrid-item-link")))
    link.click()

    token = browser.execute_script(
        "return JSON.parse(localStorage.getItem('scientia-session-authorization')).access_token")

    # Wait for table to load
    WebDriverWait(browser, MAX_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "resourcesList-items")))

    soup = BeautifulSoup(browser.page_source, "html.parser")
    # Get the table
    room_data = soup.find("ul", {"id": "ember1875"}).find_all("li")

    for room in room_data:
        name = room.find("span", {"class": "resourcesList-item-name"}).text
        room_id = room.find(
            "a", {"class": "resourcesList-item-link ember-view"})["href"].split("/")[-1]

        room_list.append({
            "name": name,
            "room_id": room_id
        })

    return {"token": token, "room_list":  room_list}


def get_availability(data, start, end):

    headers = {
        "Authorization": "Bearer " + data["token"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36"
    }
    params = {
        "StartDate": start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "EndDate": end.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "CheckSplitPermissions": False
    }

    free_spaces = []
    for room in data["room_list"]:
        res = requests.get(
            f"https://scientia-eu-v3-2-2-api-d2-02.azurewebsites.net/api/Resources/{room['room_id']}/BookingRequests",
            headers=headers,
            params=params)

        free_spaces.append({
            "name": room["name"],
            "spaces": free_space(res.json())
        })
    return free_spaces


if __name__ == "__main__":
    main()
