import os, signal
import atexit
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv # for loading environment variables from a .env file


from live_data_scrapers import fetch_live_data_council, fetch_live_data_nctx
from browser import BrowserManager
from get_stops_from_db import get_enriched_stops, get_enriched_stops_without_mongo

from flask_pymongo import PyMongo
from flask import Flask, render_template, jsonify

# loading environment variables
load_dotenv()

# load from env
user = os.getenv("MDBUSER")
pw = os.getenv("PASSW")

app = Flask (__name__)
#IMPORTANT MONGODB CONNECTION
app.config["MONGO_URI"] = f"mongodb+srv://{user}:{pw}@mymongodb.inlkhpw.mongodb.net/nctxTracking?retryWrites=true&w=majority&appName=myMongoDB"

mongo = PyMongo(app)

executor = ThreadPoolExecutor(max_workers=2)

def cleanup_resources():
    """clearing resources"""
    try:
        executor.shutdown(wait=False)
    except Exception:
        pass
    BrowserManager.quit_browser()

@app.route('/')
def home():
    """home page, renders map"""
    return render_template("stop_map.html")


@app.route('/shutdown', methods = ['GET'])
def stopServer():
    os.kill(os.getpid(), signal.SIGINT)

    return jsonify({"success": True, "message": "shutting down"})

@app.route('/api/stops', methods=['GET'])
def get_all_stops():
    """Returns all NCT stops with coordinates"""
    # stops = get_enriched_stops_without_mongo()
    stops = get_enriched_stops(mongo)
    return jsonify([{
        'stop_code': code,
        'stop_name': name,
        'lat': lat,
        'lon': lon
    } for code, name, lat, lon in stops])

@app.route('/api/stops/<stop_id>/times', methods=['GET'])
def compare_stop_times(stop_id):
    """Load NCT and bus stop times"""
    try:
        browser = BrowserManager.initialize_browser()
        if not browser:
            return jsonify({'error': 'Browser unavailable'}), 503

        nct_request = executor.submit(fetch_live_data_nctx, browser, stop_id)
        bus_stop_request = executor.submit(fetch_live_data_council, browser, stop_id)

        nct_times = nct_request.result()
        council_times = bus_stop_request.result()

        if nct_times is None:
            nct_times = []
        
        if council_times is None:
            council_times = []
        
        return jsonify({
            'council_times': council_times,
            'nct_times': nct_times
        })

    # serve the error if it applies
    except Exception as e:
        print(f"Error comparing stop times: {e}")
        return jsonify({'error': str(e),
                        'council_times': [],
                        'nct_times': [],
                        'status': 'error'
                        }), 500

try:
    app.teardown_appcontext(lambda exception: None)
    atexit.register(cleanup_resources)
except Exception:
    pass

if __name__ == "__main__":
    app.run(debug=True)
