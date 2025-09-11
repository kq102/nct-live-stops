"uses mobile App API to get distruptions"
import json
import requests # for making HTTP requests


def retrieve_nct_disruptions(stop_id):
    "uses mobile app API to retrieve times"

    API_URL = "https://nctx.arcticapi.com/network/disruptions"

    disruption_list =[]
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()

    raw_disruptions = json.loads(response.text)
    embedded_alerts = raw_disruptions["_embedded"]["alert"]

    for x in embedded_alerts:

        alert_embed = x['_embedded']
        if 'stop' in alert_embed:
            stops = alert_embed['stop']
            for s in stops:
                if s['atcoCode'] == stop_id:
                    header = x['header']
                    active_period = x['activePeriods'][0]['time_range_display']
                    disruption_list.append(f"{header}~{active_period}")
                else:
                    continue
        else:
            continue

    return disruption_list