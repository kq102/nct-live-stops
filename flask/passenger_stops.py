"""this file contains functions to download and extract stops from the passenger open data portal"""
import shutil
import os
import time
from io import BytesIO
import zipfile
import csv
import requests

# timetables api, directory to save the xml timetables to and txc namespace form xml
STOPS_API_URL = "https://data.discoverpassenger.com/operator/nctx/dataset/current/download/gtfs"
STOPS_DIRECTORY = "flask/psgr_files"

def get_and_extract(target_dir):
    """get data from BODS and extract the zip, use a temp directory for safety"""
    tmp_dir = target_dir + "_tmp"

    # if the temporary directory already exists clean it up
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

        for _ in range(10):
            if not os.path.exists(tmp_dir):
                break
            time.sleep(0.1)
        else:
            raise OSError(f"Could not remove {tmp_dir}")

    # create temp directory to download into
    os.makedirs(tmp_dir, exist_ok=True)

    # for each published Url download the zip
    try:
        with requests.get(STOPS_API_URL, stream=True, timeout=15) as response:
            response.raise_for_status()
            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(tmp_dir)

        # swap the directories after zips are downloaded and processing old stops
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.rename(tmp_dir, target_dir)

    except (requests.RequestException, zipfile.BadZipFile, OSError) as e:
        print(f"Error in get_and_extract: {e}")

def extract_stops():
    """function to open the stops.txt file that has been downloaded, extract the relevant field"""
    file_path = f"{STOPS_DIRECTORY}/stops.txt"
    if os.path.exists(file_path):
        pass

    else:
        get_and_extract(STOPS_DIRECTORY)
        extract_stops()

    # List to store extracted stop data
    stops = []

    # Open and read the file
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # read each row, find stop_id, stop_name, lat and lon
        for row in reader:
            stop = {
                "stop_code": row["stop_id"],
                "stop_name": row["stop_name"],
                "lat": float(row["stop_lat"]),
                "lon": float(row["stop_lon"])
            }
            stops.append(stop)

    return stops
