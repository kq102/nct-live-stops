"""Web scraper for live data from council journeyplanner"""
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
            departure_cards = WebDriverWait(driver, 4).until(
                EC.presence_of_all_elements_located((By.TAG_NAME,"lts-live-departure-card"))
            )
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