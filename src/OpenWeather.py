import requests
import aqi
import os
import redis
import json
from datetime import datetime
from time import localtime

API_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
APPID = os.environ.get('OW_API_KEY', False)
LAT = os.environ.get('LATITUDE', "52.205")
LONG = os.environ.get('LONGITUDE', "0.1225")

redis_client = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=6379, db=0)



class OpenWeather():

    def __init__(self):
        print("Openweather initializing")

    def fetch_current_aq(self):
        """
        Get current air quality from OpenWeather

        Returns:
            Dictionary containing weather data

        """
        params = {
            "lat": LAT,
            "lon": LONG,
            "appid": APPID,
        }

        response = requests.get(API_URL, params=params)

        # if not response.ok:
        #     error = response.json()["error"]
        #     raise WeatherAPIError(error["code"], error["message"])

        data = response.json()
        cur = data["list"][0]
        aq = cur["components"]
        raw_timestamp = cur["dt"]
        self.time_epoch = cur["dt"]
        # data_tz = data["location"]["tz_id"]
        self.pmtwo = aq["pm2_5"]
        self.pmten = aq["pm10"]

        self.timestamp = datetime.fromtimestamp(raw_timestamp)

        myaqi = aqi.to_aqi([(aqi.POLLUTANT_PM25, str(self.pmtwo)),
                            (aqi.POLLUTANT_PM10, str(self.pmten))])
        self.aqi = float(myaqi)

        self.meas = {
            "timestamp": self.timestamp,
            "pm2.5": self.pmtwo,
            "pm10": self.pmten,
            "aqi": self.aqi
        }

        return {
            'time': int(self.time_epoch),
            'measurement': self.meas
        }

    def save_measurement_to_redis(self):
        """Saves measurement to redis db"""
        redis_client.lpush('ow', json.dumps(self.fetch_current_aq(), default=str))

    def get_last_n_measurements(self):
        """Returns the last n measurements in the list"""
        return [json.loads(x) for x in redis_client.lrange('ow', 0, -1)]
