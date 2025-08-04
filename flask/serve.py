import os
from dotenv import load_dotenv # for loading environment variables from a .env file


from live_data_scrapers import fetch_live_data_council, fetch_live_data_nctx, driver_quit
from browser import initialize_app_data
from get_stops_from_db import get_enriched_stops, get_enriched_stops_without_mongo

from flask_pymongo import PyMongo
from flask import Flask, render_template, jsonify

# loading environment variables
load_dotenv()

# load from env
#user = os.getenv("MDBUSER")
#pw = os.getenv("PASSW")

app = Flask (__name__)
# IMPORTANT MONGODB CONNECTION
#app.config["MONGO_URI"] = f"mongodb+srv://{user}:{pw}@mymongodb.inlkhpw.mongodb.net/nctxTracking?retryWrites=true&w=majority&appName=myMongoDB"
#app.config["SCHEDULER_API_ENABLED"] = True
#app.config['SCHEDULER_TIMEZONE'] = "Europe/London"

#mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template("stop_map.html")

@app.route('/get_all_stops')
def get_all_stops():
    """Returns all NCT stops with coordinates"""
    stops = get_enriched_stops_without_mongo()
    # stops = get_enriched_stops(mongo)
    return jsonify([{
        'stop_code': code,
        'stop_name': name,
        'lat': lat,
        'lon': lon
    } for code, name, lat, lon in stops])

@app.route('/compare_stop_times/<stop_id>')
def compare_stop_times(stop_id):
    """Compares times from NCT and Council sources"""
    try:
        browser = initialize_app_data()
        council_times = fetch_live_data_council(browser,stop_id)
        nct_times = fetch_live_data_nctx(browser,stop_id)
        
        return jsonify({
            'council_times': council_times,
            'nct_times': nct_times
        })
    
    # serve the error if it applies
    except Exception as e:
        print(f"Error comparing stop times: {e}")
        return jsonify({'error': str(e)}), 500
    
    # finally quit the driver
    finally:
        driver_quit(browser)

if __name__ == "__main__":
    app.run(debug=True)
