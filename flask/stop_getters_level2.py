"""to get stops"""
from stop_getters_level1 import get_stop_coordinates

# uses area_stops to get the stop location coordinates for the stops NCT uses (using naptan api)
def get_enriched_stops(mongo):
    """gets the co-ords for the stops using get_stop_coordinates function in area_stops module"""
    stops_lookup = get_stops_lookup(mongo)
    enriched_stops_cache = get_stop_coordinates(stops_lookup)
    return enriched_stops_cache

# retrieves all stops that NCT uses from the database and caches it
def get_stops_lookup(mongo):
    """returns stop from db document"""
    stops_cursor = mongo.db.nct_stops.find({}, {"_id": 1, "stop_name": 1, "locality":1})
    stops_lookup_cache = {stop["_id"]: stop for stop in stops_cursor}
    return stops_lookup_cache