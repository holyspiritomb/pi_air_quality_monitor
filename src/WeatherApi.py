import requests
import aqi
import os
import redis
import json
from datetime import datetime


WEATHERAPI_URL = "http://api.weatherapi.com/v1/current.json"
WEATHERAPI_KEY = os.environ.get('WEATHERAPI_KEY', False)
LOCATION = os.environ.get('LOCATION', "Philadelphia")

redis_client = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=6379, db=0)


class WeatherAPIError(Exception):
    """Raised when WeatherAPI returns an error response."""
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"WeatherAPI error {code}: {message}")


class WeatherApi():

    def __init__(self):
        print("WeatherAPI")

    def get_current_weather(self):
        """
        Get current weather for a location.

        Returns:
            Dictionary containing our desired weather data

        Raises:
            WeatherAPIError: If the API returns an error
        """
        params = {
            "key": WEATHERAPI_KEY,
            "q": LOCATION,
            "aqi": "yes",
        }

        response = requests.get(WEATHERAPI_URL, params=params)

        if not response.ok:
            error = response.json()["error"]
            raise WeatherAPIError(error["code"], error["message"])

        data = response.json()
        cur = data["current"]
        aq = cur["air_quality"]
        raw_timestamp = cur["last_updated"]
        self.time_epoch = cur["last_updated_epoch"]
        # data_tz = data["location"]["tz_id"]
        self.pmtwo = aq["pm2_5"]
        self.pmten = aq["pm10"]

        self.timestamp = datetime.strptime(raw_timestamp, '%Y-%m-%d %H:%M')

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
        redis_client.lpush('wa', json.dumps(self.get_current_weather(), default=str))

    def get_last_n_measurements(self):
        """Returns the last n measurements in the list"""
        return [json.loads(x) for x in redis_client.lrange('wa', 0, -1)]
