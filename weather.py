import openmeteo_requests
import pandas as pd
import requests_cache
from numpy.ma.core import around
from retry_requests import retry


def get_weather():
    cache_session = requests_cache.CachedSession('.cache', expire_after=600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 47.2313,
        "longitude": 39.7233,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "current": "temperature_2m",
        "timezone": "Europe/Moscow",
        "forecast_days": 1,
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    current = response.Current()

    #current_temp = int(current.Variables(0).Value())
    current_temp = (current.Variables(0).Value())

    daily = response.Daily()


    #max_temp = int(daily.Variables(0).ValuesAsNumpy()[0])
    max_temp = (daily.Variables(0).ValuesAsNumpy()[0])
    #min_temp = int(daily.Variables(1).ValuesAsNumpy()[0])
    min_temp = (daily.Variables(1).ValuesAsNumpy()[0])
    return {
        "current": round(current_temp, 2),
        "max": round(max_temp),
        "min": round(min_temp),
    }
