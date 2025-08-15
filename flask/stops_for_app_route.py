from get_stops_from_db import get_enriched_stops, get_enriched_stops_without_mongo
from flask import jsonify

def get_all_stops(mongo):
    """Returns all NCT stops with coordinates"""
    #stops = get_enriched_stops_without_mongo()
    stops = get_enriched_stops(mongo)
    return jsonify([{
        'stop_code': code,
        'stop_name': name,
        'lat': lat,
        'lon': lon
    } for code, name, lat, lon in stops])