"""web scraper for live data"""

import time

from selenium.webdriver.common.by import By #for css selcetion

def fetch_live_data_council(driver, stop_id):
    """sets up chrome and selenium to get stop live data from nottinghamshire gov"""

    council_data_list = []
    ## nottinghamshire county council gov site
    council_url = f"https://journeyplanner.nottinghamshire.gov.uk/departures/liveDepartures?stopId={stop_id}"

    driver.get(council_url)

    time.sleep(2.2)  # await js loading

    # redundant use of stop names
    # council_stop_name = driver.find_element(By.TAG_NAME, "lts-stop-name").text
    departure_cards = driver.find_elements(By.TAG_NAME, "lts-live-departure-card")

    # council_data_list.append(council_stop_name)

    # loop through the departure cards and get just the text from the relevant fields
    for card in departure_cards:
        cells=card.find_elements(By.XPATH,".//div[@role='gridcell']")
        
        driver.execute_script("arguments[0].scrollIntoView();", card)

        route_number = cells[0].text.strip() # route number
        destination = cells[1].text.strip() # destination
        arrival_time = cells[3].text.strip() # time
        council_data_list.append(f"{route_number}-{destination}-{arrival_time}")

    return council_data_list


def fetch_live_data_nctx(driver, stop_id):
    """function gets html for the live data from nctx.co.uk and processes it immediately"""
    nct_data_list = []
    live_or_not = None

    nct_url = f"https://www.nctx.co.uk/stops/{stop_id}"

    driver.get(nct_url)
    
    time.sleep(1)  # await js loading

    # redundant stop_name data
    # stop_name = driver.find_element(By.CLASS_NAME, "place-info-banner__name").text.strip()
    # stop_code = driver.find_element(By.CLASS_NAME, "place-info-banner__tablet").text.strip()
    
    departures = driver.find_elements(By.CLASS_NAME, "departure-board__item")

    # redundant appendage to list of stop names
    # live_times_from_stop_name = f"{stop_name} {stop_code}"
    # nct_data_list.append(live_times_from_stop_name)

    # each line get the route, dest, time & css colour to determine if time is scheduled or not
    for line in departures:
        route = line.find_element(By.CLASS_NAME, "single-visit__name").text
        destination = line.find_element(By.CLASS_NAME, "single-visit__description").text
        arrival_element = line.find_element(By.CLASS_NAME, "single-visit__arrival-time__cell")
        arrival = arrival_element.text

        # Get the background color of the arrival cell
        bg_color = arrival_element.value_of_css_property("background-color")
        if bg_color == "rgba(223, 240, 216, 1)":
            live_or_not = "(Live)"
        else:
            live_or_not = ("(Schedueled)")

        nct_data_list.append(f"{route}-{destination}-{arrival}-{live_or_not}")

    return nct_data_list

def driver_quit(driver):
    driver.quit()