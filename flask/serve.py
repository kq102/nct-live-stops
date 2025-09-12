"main file for initializing system "
import os
import signal
import atexit
import time
from concurrent.futures import ThreadPoolExecutor
from live_data_scrapers import fetch_live_data_council
from nct_ping import retrive_nct_stop_times
from disruptions import retrieve_nct_disruptions
# from get_stops_from_db import get_enriched_stops, get_enriched_stops_without_mongo
from passenger_stops import STOPS_DIRECTORY, get_and_extract,  extract_stops
from flask_apscheduler import APScheduler # for the important scheduler jobs
from apscheduler.schedulers.background import BackgroundScheduler # scheduler jobs keep running in bg
from flask import Flask, render_template, jsonify

executor = ThreadPoolExecutor(max_workers=2)

app = Flask (__name__)
app.config["SCHEDULER_API_ENABLED"] = True
app.config['SCHEDULER_TIMEZONE'] = "Europe/London"

scheduler = APScheduler(BackgroundScheduler(daemon=True))
scheduler.init_app(app)
scheduler.start()

def cleanup_resources():
    """clearing resources"""
    try:
        executor.shutdown(wait=False)
    except Exception:
        pass

@app.route('/')
def home():
    """home page, renders map"""
    return render_template("stop_map.html")

@app.route('/shutdown', methods = ['GET'])
def stopServer():
    """kill server"""
    os.kill(os.getpid(), signal.SIGINT)

    return jsonify({"success": True, "message": "shutting down"})

@app.route('/api/stops', methods=['GET'])
def get_all_stops():
    """Returns all NCT stops with coordinates"""
    # stops = get_enriched_stops_without_mongo()
    # stops = get_enriched_stops(mongo)
    time.sleep(0.2)
    stops = extract_stops()
    return jsonify(stops)

@app.route('/api/stops/<stop_id>/times', methods=['GET'])
def compare_stop_times(stop_id):
    """Load NCT and bus stop times"""
    try:
        nct_times_request = executor.submit(retrive_nct_stop_times,stop_id)
        nct_times = nct_times_request.result(timeout=60)

        bus_stop_request = executor.submit(fetch_live_data_council, stop_id)
        council_times = bus_stop_request.result(timeout=60)
        
        stop_disruptions = retrieve_nct_disruptions(stop_id)

        return jsonify({
            'council_times': council_times,
            'nct_times': nct_times,
            'stop_disruptions': stop_disruptions
        })

    # serve the error if it applies
    except Exception as e:
        print(f"Error comparing stop times: {e}")
        return jsonify({'error': str(e)}), 500

try:
    app.teardown_appcontext(lambda exception: None)
    atexit.register(cleanup_resources)
except Exception:
    pass

@scheduler.task('interval', id='update_stops', seconds=7200, max_instances=1, misfire_grace_time=1000)
def scheduled_stop_update():
    """scheduled to call function for a daily stops update"""
    # get and extract the timetable XML files from zip files
    for attempt in range(5):
        try:
            get_and_extract(STOPS_DIRECTORY)
            print(f"\n--- Extract attempt: {attempt+1} successful ---")
        except Exception as e:
            print(f"\n--- Attempt {attempt+1}: Error: {e} ---")
            time.sleep(2)

    print("done")

if __name__ == "__main__":
    app.run(debug=True)
