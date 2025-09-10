"uses mobile App API to get stop times"
import requests # for making HTTP requests
import json

def retrive_nct_stop_times(stop_id):
    "uses mobile app API to retrieve times"

    API_URL = f"https://nctx.arcticapi.com/network/stops/{stop_id}/visits"

    nct_data_list =[]
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()

    raw_times = json.loads(response.text)
    embedded_times = raw_times["_embedded"]["timetable:visit"]

    for x in embedded_times:
        line_name = x['_links']['transmodel:line']['name'] if '_links' in x else ""
        destination = x['destinationName'] if 'destinationName' in x else ""
        # aimedDeparture = x['aimedDepartureTime'] if 'aimedDepartureTime' in x else ""
        # expectedDeparture = x['expectedDepartureTime'] if 'expectedDepartureTime' in x else ""
        is_real_time = x['isRealTime'] if 'isRealTime' in x else ""
        display_time = x['displayTime'] if "displayTime" in x else ""

        # objAiDe = datetime.strptime(aimedDeparture,"%Y-%m-%dT%H:%M:%S%z")
        # objExDe = datetime.strptime(expectedDeparture,"%Y-%m-%dT%H:%M:%S%z") if expectedDeparture != "" else objAiDe
        if is_real_time is True:
            live_or_not = "rgba(223, 240, 216, 1)"
        else:
            live_or_not = "#f5f5f5"

        nct_data_list.append(f"{line_name}~{destination}~{display_time}~{live_or_not}")

    return(nct_data_list)
