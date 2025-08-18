"""now thread safe web scraper for live data"""

from threading import Lock
from selenium.webdriver.common.by import By #for css selcetion
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


scraper_lock = Lock()

def fetch_live_data_council(driver, stop_id):
    """sets up chrome and selenium to get stop live data from nottinghamshire gov"""
    with scraper_lock:
        try:

            # list to append the times to at end of fucntion
            council_data_list = []

            ## nottinghamshire county council gov site
            council_url = f"https://journeyplanner.nottinghamshire.gov.uk/departures/liveDepartures?stopId={stop_id}"
            driver.get(council_url)
            # use the driver to load the page the page the in the virtual browser

            ## wait until prescence of an element is detected before continuing
            try:
                WebDriverWait(driver, 2.5).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME,"lts-live-departure-card"))
                )
            except Exception as e:
                print(f"ERROR: {e}")


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
                council_data_list.append(f"{route_number}~{destination}~{arrival_time}")

            return council_data_list
        except Exception as e:
            print(f"error fetching council data: {e}")
            return []


def fetch_live_data_nctx(driver, stop_id):
    """function gets html for the live data from nctx.co.uk and processes it immediately"""
    with scraper_lock:
        try:
            nct_data_list = []
            live_or_not = None

            nct_url = f"https://www.nctx.co.uk/stops/{stop_id}"

            driver.get(nct_url)
            
            try:
                WebDriverWait(driver, 2.5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,"departure-board__item"))
                )
            except Exception as e:
                print(f"ERROR: {e}")
                
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
                    live_or_not = "rgba(223, 240, 216, 1)"
                else:
                    live_or_not = "#f5f5f5"

                nct_data_list.append(f"{route}~{destination}~{arrival}~{live_or_not}")

            return nct_data_list
        except Exception as e:
            print(f"error fetching NCT data{e}")
            return []