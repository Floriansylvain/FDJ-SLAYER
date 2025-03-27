"""
Weather module for entropy generation
"""

import time
import hashlib
import random
import openmeteo_requests
import requests_cache
from retry_requests import retry

from constants import OPENMETEO_API_URL, OPENMETEO_HOURLY_PARAMS


class Weather:
    """Handles weather data retrieval for entropy generation"""

    def __init__(self):
        self.api_url = OPENMETEO_API_URL
        self.hourly_params = OPENMETEO_HOURLY_PARAMS

    def _fetch_weather_api(self, params):
        """Internal function to make Open-Meteo API requests"""
        cache_session = requests_cache.CachedSession('.cache', expire_after=60)
        retry_session = retry(cache_session, retries=2, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        return openmeteo.weather_api(self.api_url, params=params)

    def _get_weather_data(self):
        """Internal function that retrieves weather data from API"""
        params = {
            "latitude": random.uniform(-70, 70),
            "longitude": random.uniform(-180, 180),
            "hourly": random.sample(self.hourly_params, random.randint(3, 6)),
            "timezone": "auto"
        }

        responses = self._fetch_weather_api(params)
        entropy_values = []
        for i in range(len(params["hourly"])):
            var_values = responses[0].Hourly().Variables(i).ValuesAsNumpy()
            entropy_values.extend(var_values.tolist())

        weather_str = "".join([str(v) for v in entropy_values])
        return hashlib.sha256(weather_str.encode()).hexdigest()

    def get_weather_entropy(self):
        """Retrieves weather data as additional source of entropy"""
        try:
            return self._get_weather_data()
        except Exception as e:
            print(f"Error retrieving weather data: {e}")
            fallback = f"weather_fallback_{time.time()}_{random.getrandbits(64)}"
            return hashlib.sha256(fallback.encode()).hexdigest()
