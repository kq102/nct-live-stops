"""see functoon definiton"""
import json


def json_stops_lookup():
    """loads stops from a json file to test locally rather than using monogoDB"""
    with open('flask/json_files/stops.json') as stops_json:
        data = json.load(stops_json)

    return data

json_stops_lookup()
