import os
import time
from zoneinfo import ZoneInfo
from datetime import datetime
from flask import Flask, request, jsonify, render_template, flash
from AirQualityMonitor import AirQualityMonitor
from WeatherApi import WeatherApi
from OpenWeather import OpenWeather
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import redis
import atexit
from flask_cors import CORS, cross_origin

INTERVAL = int(os.environ.get('INTERVAL', 120))
WA_KEY = os.environ.get('WEATHERAPI_KEY', False)
OW_KEY = os.environ.get('OW_API_KEY', False)
SAMPLES = int(os.environ.get('SAMPLES', 30))


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
aqm = AirQualityMonitor()
wa = WeatherApi()
ow = OpenWeather()

# FIX: In the event of IncompleteReadException, log it and stop the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=aqm.save_measurement_to_redis, trigger="interval", seconds=INTERVAL, id="take_measurement")
# Don't schedule the job of fetching WeatherAPI data unless there is a key
if OW_KEY:
    scheduler.add_job(func=ow.save_measurement_to_redis, trigger='cron', minute='*/15', id="fetch_outside")
# if WA_KEY:
#     scheduler.add_job(func=wa.save_measurement_to_redis, trigger='cron', minute='*/15', id="fetch_outside")
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def reconfigure_data(measurement):
    """Reconfigures data for chart.js"""
    current = int(time.time())
    # TODO: make number of measurements displayed configurable
    measurement = measurement[:SAMPLES]
    measurement.reverse()
    return {
        'labels': [x['measurement']['timestamp'] for x in measurement],
        'aqi': {
            'label': 'aqi',
            'data': [x['measurement']['aqi'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#181d27',
            'borderColor': '#181d27',
            'borderWidth': 1
        },
        'pm10': {
            'label': 'pm10',
            'data': [x['measurement']['pm10'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#cc0000',
            'borderColor': '#cc0000',
            'borderWidth': 1
        },
        'pm2': {
            'label': 'pm2.5',
            'data': [x['measurement']['pm2.5'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#42C0FB',
            'borderColor': '#42C0FB',
            'borderWidth': 1
        },
    }


def reconfigure_outside_data(measurement):
    """Reconfigures data for chart.js"""
    measurement = measurement[:24]
    measurement.reverse()
    return {
        'labels': [x['measurement']['timestamp'] for x in measurement],
        'aqi': {
            'label': 'aqi',
            'data': [x['measurement']['aqi'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#181d27',
            'borderColor': '#181d27',
            'borderWidth': 1
        },
        'pm10': {
            'label': 'pm10',
            'data': [x['measurement']['pm10'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#cc0000',
            'borderColor': '#cc0000',
            'borderWidth': 1
        },
        'pm2': {
            'label': 'pm2.5',
            'data': [x['measurement']['pm2.5'] for x in measurement],
            'parsing': 'false',
            'backgroundColor': '#42C0FB',
            'borderColor': '#42C0FB',
            'borderWidth': 1
        },
    }


@app.route('/')
def index():
    """Index page for the application"""
    context = {
        'historical': reconfigure_data(aqm.get_last_n_measurements())
    }
    return render_template('index.html', context=context)


@app.route('/outside')
def outside():
    """Outside page for the application"""
    if OW_KEY:
        context = {
            # Sensor data is used to determine x-axis limits
            'historical': reconfigure_data(aqm.get_last_n_measurements()),
            'outside': reconfigure_outside_data(ow.get_last_n_measurements())
        }
        # Only render if key is actually present.
        return render_template('outside.html', context=context)
    else:
        return False
    # return render_template('outside.html', context=context)


@app.route('/api/')
@cross_origin()
def api():
    """Returns historical data from the sensor"""
    if not OW_KEY:
        context = {
            'historical': reconfigure_data(aqm.get_last_n_measurements())
        }
    else:
        context = {
            'historical': reconfigure_data(aqm.get_last_n_measurements()),
            'outside': reconfigure_outside_data(ow.get_last_n_measurements())
        }
    return jsonify(context)


@app.route('/api/now/')
def api_now():
    """Returns latest data from the sensor"""
    meas = aqm.get_measurement()

    save = request.args.get('save')

    if save == '1':
        aqm.save_measurement_to_redis(meas)

    context = {
        'current': meas
    }
    return jsonify(context)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))
