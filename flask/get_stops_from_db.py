# """to get stops"""
# from get_stop_co_ords import get_stop_coordinates
# from local_testing_json import json_stops_lookup

# # uses area_stops to get the stop location coordinates for the stops NCT uses (using naptan api)
# def get_enriched_stops(mongo):
#     """gets the co-ords for the stops using get_stop_coordinates function in area_stops module"""
#     stops_lookup = get_stops_lookup(mongo)
#     enriched_stops = get_stop_coordinates(stops_lookup)
#     return enriched_stops

# # retrieves all stops that NCT uses from the database and caches it
# def get_stops_lookup(mongo):
#     """returns stop from db document"""
#     stops_cursor = mongo.db.nct_stops.find({}, {"_id": 1, "stop_name": 1, "locality":1})
#     stops_lookup = {stop["_id"]: stop for stop in stops_cursor}
#     return stops_lookup

# def get_enriched_stops_without_mongo():
#     """uses the local file instead of mongo as a dictionary"""
#     stops_lookup = json_stops_lookup()
#     enriched_stops = get_stop_coordinates(stops_lookup)
#     return enriched_stops
