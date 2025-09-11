# """functions to get the stop co-ordinates from naptan & process them against NCT stops from"""
# import csv
# import requests

# def stream_naptan_csv(url):
#     """ streaming file function"""
#     with requests.get(url, stream=True, timeout=10) as r:
#         r.raise_for_status()
#         # Stream lines and decode as utf-8
#         lines = (line.decode('utf-8') for line in r.iter_lines())
#         reader = csv.DictReader(lines)

#         yield from reader  # process each row one at a time

# def get_stop_coordinates(stops_lookup):
#     """use stops file to validate bus stop existance from api & get coordinates for it"""

#     naptan_url = "https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv&atcoAreaCodes=339%2C330%2C260"
#     # Prepare results
#     results = []

#     nct_stops = dict(stops_lookup)

#     # Stream the NaPTAN CSV and match as we go
#     for row in stream_naptan_csv(naptan_url):

#         stop_code = row["ATCOCode"]

#         if stop_code in nct_stops:

#             stop_info = nct_stops[stop_code]

#             lat = row.get("Latitude")
#             lon = row.get("Longitude")
#             bearing = row.get("Bearing")

#             stop_info["latitude"] = lat
#             stop_info["longitude"] = lon
#             stop_info["bearing"] = bearing

#             results.append((stop_code, stop_info["stop_name"], lat, lon))
            
#             del nct_stops[stop_code]

#     # For any stops not found in NaPTAN, add with None lat/lon
#     for stop_code, stop_info in nct_stops.items():
#         results.append((stop_code, stop_info["stop_name"], None, None))

#     print("returning the stops...")
#     return results
