#!/usr/bin/env python
from collections import OrderedDict
from datetime import datetime
import requests

from settings import api_key, latitude, longitude


base_url = 'https://api.darksky.net/forecast/{}/{},{}'
normal_output_str = 'There will be rain at {}, the forecast is showing {}.'
rain_now_output_str = 'It\'s raining now!  The forecast is showing {}.'
precip_threshold = 0.3

url = base_url.format(api_key, latitude, longitude)
forecast = requests.get(url).json()

time_fmt = OrderedDict()
time_fmt['minutely'] = '%I:%M %p'
time_fmt['hourly'] = '%I %p'
time_fmt['daily'] = '%A'


def convert_time(epoch_time):
    return datetime.fromtimestamp(epoch_time)


def get_rain_forecast(forecast):
    try:
        return rain_next['summary'].lower()
    except KeyError:
        return rain_next['precipType'].lower()


def format_output(rain_next, period):
    rain_time = convert_time(rain_next['time'])
    rain_forecast = get_rain_forecast(rain_next)
    delta = (rain_time - datetime.now()).total_seconds()

    if delta <= 60:
        return rain_now_output_str.format(rain_forecast)

    rain_time_str = rain_time.strftime(time_fmt[period])
    return normal_output_str.format(rain_time_str, rain_forecast)


for period in time_fmt.keys():
    rain_next = next(
        (
            fc for fc in forecast[period]['data']
            if fc['precipProbability'] > precip_threshold
        ),
        None,
    )
    if rain_next:
        break

print(format_output(rain_next, period))
