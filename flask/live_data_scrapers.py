"""Web scraper for live data from council journeyplanner"""
import json
import os
from datetime import datetime, timezone
import requests
from dateutil import parser
import pytz
from dotenv import load_dotenv # for loading environment variables from a .env file

load_dotenv()
key = os.getenv("COUNCIL_SUB_KEY")

uk_timezone = pytz.timezone("Europe/London")

class DepartureProcessor:
    """handling the api's departure data"""
    def __init__(self):
        self.now = datetime.now(uk_timezone)
        # sets the current time for the processor class functions

    def get_api_response(self, stop_id):
        """getting the council api response"""
        local_offset = self.now.utcoffset()
        client_offset_ms = int(-local_offset.total_seconds() * 1000)

        utc_time = self.now.astimezone(timezone.utc)
        formatted_time = utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        url = "https://api-manager-hub-uksouth-1.azure-api.net/d2n2/production/lts/lts/v1/public/departures"
        headers = {
            "Ocp-Apim-Subscription-Key": f"{key}",
            "Content-Type": "application/json"
        }
        payload = {
            "clientTimeZoneOffsetInMS": client_offset_ms,
            "departureDate": f"{formatted_time}",
            "departureTime": f"{formatted_time}",
            "stopIds": [stop_id],
            "stopType": "BUS_STOP",
            "stopName": "",  # optional, can be omitted
            "crsCode": None,
            "requestTime": f"{formatted_time}",
            "departureOrArrival": "DEPARTURE",
            "refresh": False
        }
        # POST request containing url, payload and headers containg important subscription key
        response = requests.post(url, json=payload, headers=headers, timeout=20)

        # get data from response
        data = response.json()

        return data

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

        if due_time == "0 mins":
            due_time = "Due"
        # removes departures that are in the past
        # recalculate realtime departures in minutes rather than HH:MM
        # adds realtime css colour highlight apply
        return f"{departure_data['serviceNumber']}~{departure_data['destination']}~{due_time}~{live_or_not}"

def processing_api_response(response_body):
    """Process API response and extract departure information"""
    # loads in the json response and then goes into the stopDepartures section for further processing
    try:
        result = response_body['stopDepartures']
        return result
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing API response: {e}")
        return []

def fetch_live_data_council(stop_id):
    """sets up chrome and selenium to get stop live data from nottinghamshire gov"""
    departures_list = []
    try:
        # establish class process and list for retrival and holding the departures
        processor = DepartureProcessor()

        # Get network response for the api using function.
        response_body = processor.get_api_response(stop_id)

        # enters the actual stopDepartures section of the API response via funtion
        stop_departures = processing_api_response(response_body)

        # for each departure that is in the api response, extract information and format it
        for departure in stop_departures[:26]:
            real_time_uk, is_real_time = processor.process_departure(departure)

            formatted_departure = processor.formatting_departure_entry(departure,real_time_uk, is_real_time)

            if formatted_departure:
                departures_list.append(formatted_departure)

    except Exception as e:
        print(f"error fetching council data: {e}")

    return departures_list
