"""Web scraper for live data from council journeyplanner"""
import json
from datetime import datetime
from threading import Lock
from dateutil import parser, tz
import pytz
from selenium.webdriver.common.by import By #for css selcetion
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

scraper_lock = Lock()
uk_timezone = pytz.timezone("Europe/London")

class DepartureProcessor:
    """handling the api's departure data"""
    def __init__(self):
        self.now = datetime.now(uk_timezone)
        # this is the current time

    def process_departure(self, departure_data):
        """Processing a single departure time entry"""
        scheduled_dep = departure_data['scheduledDeparture']
        real_time_dep = departure_data['realTimeDeparture'] or scheduled_dep
        real_time_obj = parser.parse(real_time_dep)
        # gets the scheduled time and real time if it applies
        # also return a boolean object if the realtime exists
        return real_time_obj.astimezone(uk_timezone), bool(departure_data['realTimeDeparture'])

    def formatting_departure_entry(self, departure_data, real_time_uk, is_real_time):
        """formatting a single time entry"""
        if not real_time_uk > self.now:
            return None

        if is_real_time:
            time_diff = real_time_uk - self.now
            due_time = str(int(time_diff.total_seconds() // 60)) + " mins"
            live_or_not = "#dff0d8"

        else:
            due_time = real_time_uk.strftime("%H:%M")
            live_or_not = "#f5f5f5"
        # removes departures that are in the past
        # recalculate realtime departures in minutes rather than HH:MM
        # adds realtime css colour highlight apply
        return f"{departure_data['serviceNumber']}~{departure_data['destination']}~{due_time}~{live_or_not}"

def processing_api_response(response_body):
    """Process API response and extract departure information"""
    # loads in the json response and then goes into the stopDepartures section for further processing
    try:
        result = json.loads(response_body["body"])
        return result.get("stopDepartures", [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing API response: {e}")
        return []
    
def getting_api_response(driver, log_entry):
    """extracting the api response from log entry"""
    # loads the logs from chrome, finds the council API response for departures
    # executes driver command to get the body of this response for processing
    try:
        log_data = json.loads(log_entry['message'])
        if not all(key in log_data.get('message', {}) for key in ['method', 'params']):
            return None

        if log_data['message']['method'] != 'Network.responseReceived':
            return None

        response = log_data['message']['params']['response']
        if 'api-manager-hub-uksouth-1.azure-api.net/d2n2/production/lts/lts/v1/public/departures' not in response.get('url', ''):
            return None

        request_id = log_data['message']['params']['requestId']
        return driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
    
    except Exception as e:
        print(f"Error getting API response: {e}")
        return None

def fetch_live_data_council(driver, stop_id):
    """sets up chrome and selenium to get stop live data from nottinghamshire gov"""
    # makes the request to the council journey planner site first
    with scraper_lock:
        try:
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})

            ## nottinghamshire county council gov site
            council_url = f"https://journeyplanner.nottinghamshire.gov.uk/departures/liveDepartures?stopId={stop_id}"
            driver.get(council_url)

            # use the driver to load the page the page the in the virtual browser
            ## wait until prescence of an element is detected before continuing
            #departure_cards =
            WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.TAG_NAME,"lts-live-departure-card"))
            )

            # establish class process and list for holding the departures
            processor = DepartureProcessor()
            departures_list = []

            # Get network response for the api using function.
            for log_entry in driver.get_log('performance'):
                response_body = getting_api_response(driver, log_entry)
                if not response_body:
                    continue

                # enters the actual departures section of the API response via funtion
                stop_departures = processing_api_response(response_body)

                # for each departure that is in the api response, extract information and format it
                for departure in stop_departures:
                    real_time_uk, is_real_time = processor.process_departure(departure)

                    formatted_departure = processor.formatting_departure_entry(departure,real_time_uk, is_real_time)

                    if formatted_departure:
                        departures_list.append(formatted_departure)

            return departures_list
        except Exception as e:
            print(f"error fetching council data: {e}")
            return []
        finally:
            # Disable network tracking
            driver.execute_cdp_cmd('Network.disable', {})
