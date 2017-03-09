#!/usr/bin/env python
"""
Simple script to hook into the DarkSky API and tell the user when it will
rain next.

Expects a settings.py file in the same directory with the contents:
api_key = ''
latitude = ''
longitude = ''

Powered by Dark Sky https://darksky.net/poweredby
"""

from collections import OrderedDict
from datetime import datetime
import requests

from settings import api_key, latitude, longitude


base_url = 'https://api.darksky.net/forecast/{}/{},{}'
normal_output_str = 'There will be rain at {}, the forecast is showing {}'
rain_now_output_str = 'It\'s raining now!  The forecast is showing {}'
no_rain_output_str = 'No rain forecast for the next week.'
precip_threshold = 0.3

time_fmt = OrderedDict()
time_fmt['minutely'] = '%I:%M %p'
time_fmt['hourly'] = '%I %p'
time_fmt['daily'] = '%A'


def convert_time(epoch_time):
    return datetime.fromtimestamp(epoch_time)


def get_forecast():
    url = base_url.format(api_key, latitude, longitude)
    forecast = requests.get(url).json()

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
    return period, rain_next


def get_rain_forecast(forecast):
    try:
        return forecast['summary'].lower()
    except KeyError:
        return forecast['precipType'].lower()


def format_output(rain_next, period):
    if not rain_next:
        return no_rain_output_str

    rain_time = convert_time(rain_next['time'])
    rain_forecast = get_rain_forecast(rain_next)
    delta = (rain_time - datetime.now()).total_seconds()

    if delta <= 60 and period is not 'daily':
        return rain_now_output_str.format(rain_forecast)

    rain_time_str = rain_time.strftime(time_fmt[period])

    if period == 'daily':
        output_str = normal_output_str.replace('at', 'on')
        return output_str.format(rain_time_str, rain_forecast)
    return normal_output_str.format(rain_time_str, rain_forecast)


if __name__ == '__main__':
    period, rain_next = get_forecast()
    print(format_output(rain_next, period))
