from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from free_space import free_space
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from graph_viz import generate
from pytz import timezone, utc
import requests
import argparse
from pyvirtualdisplay import Display
import logger
import traceback


LOGIN_PAGE = "https://scientia-rb-rhul.azurewebsites.net/app/booking-types"
MAX_WAIT = 15
LOCAL_TIME_ZONE = "Europe/London"


def main():
    display = Display(visible=0, size=(1080, 1920))
    display.start()

    args = get_login_details()

    chromedriver_autoinstaller.install()

    browser = webdriver.Chrome()

    login(browser, args)
    data = get_room_ids(browser)
    browser.close()
    spaces = get_availability(
        data, args["start_date"], args["start_date"] + timedelta(days=1))

    generate(spaces, args["start_date"])


def get_login_details():
    start_time = datetime.now().date()

    parser = argparse.ArgumentParser(description="Mark attendance for RHUL")

    parser.add_argument("-u", "--username",
                        help="Full username for RHUL", required=True)

    parser.add_argument("-p", "--password",
                        help="Password for RHUL", required=True)

    parser.add_argument("-s", "--start-date",
                        help="Date to start searching from", type=datetime.fromisoformat, default=start_time)

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

    # Get JWT Token
    token = browser.execute_script(
        "return JSON.parse(localStorage.getItem('scientia-session-authorization')).access_token")

    # Wait for table to load
    WebDriverWait(browser, MAX_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "resourcesList-items")))

    soup = BeautifulSoup(browser.page_source, "html.parser")

    # Get the table
    room_data = soup.find(
        "ul", {"class": "ember-view resourcesList-items"}).find_all("li")

    # Extract date from table
    for room in room_data:
        name = room.find("span", {"class": "resourcesList-item-name"}).text
        room_id = room.find(
            "a", {"class": "resourcesList-item-link ember-view"})["href"].split("/")[-1]

        room_list.append({
            "name": name,
            "room_id": room_id
        })

    return {"token": token, "room_list":  room_list}


def get_availability(data, start_date, end_date):
    # Set London to adjust for daylight saving timezone
    start = timezone(LOCAL_TIME_ZONE).localize(
        datetime.combine(start_date, datetime.min.time()))

    end = timezone(LOCAL_TIME_ZONE).localize(
        datetime.combine(end_date, datetime.min.time()))

    headers = {
        "Authorization": "Bearer " + data["token"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36"
    }
    params = {
        "StartDate": start.astimezone(utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "EndDate": end.astimezone(utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "CheckSplitPermissions": False
    }

    free_spaces = []
    for room in data["room_list"]:
        res = requests.get(
            f"https://scientia-eu-v3-2-2-api-d2-02.azurewebsites.net/api/Resources/{room['room_id']}/BookingRequests",
            headers=headers,
            params=params)

        spaces = free_space(res.json(), start)
        for space in spaces:
            free_spaces.append({
                "room": room["name"],
                "start": space["StartDateTime"],
                "end": space["EndDateTime"]
            })
    return free_spaces


if __name__ == "__main__":
    try:
        main()
    except:
        err = traceback.format_exc()
        logger.logError(err)
