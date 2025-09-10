import requests
import json

def notts_derby_rslepi_test(stop_id):
    API_URL = f"http://publicnottsderby.rslepi.co.uk/departureboards/mepiDepartureBoard.aspx?id={stop_id}"

    rslepi_data_list =[]
    response = requests.get(API_URL, timeout=8)
    response.raise_for_status()


    print(response.text)


notts_derby_rslepi_test(1)