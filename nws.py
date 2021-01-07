# vim: ts=4 sw=4 expandtab

import io
import re
import sys
import textwrap
import os.path
import urllib.request
import xml.etree.ElementTree

url = 'https://forecast.weather.gov/MapClick.php?lat=39.54&lon=-104.91&unit=0&lg=english&FcstType=dwml'

layout_key = 'k-p12h-n14-1'

def get_forecast_location(forecast):
    location = forecast.find('./location')
    assert location is not None
    point = location.find('./point')
    assert point is not None

def get_forecast_maximum_temperatures(parameters):
    return parameters.findall('./temperature[@type="maximum"]/value')

def get_forecast_minimum_temperatures(parameters):
    return parameters.findall('./temperature[@type="minimum"]/value')

def get_forecast_weather(parameters):
    return parameters.findall('./weather[@time-layout="' + layout_key + '"]/weather-conditions')

def get_icon(url):
    filename = '/tmp/' + re.sub(r'.*/', '', url.text)
    if not os.path.isfile(filename):
        urllib.request.urlretrieve(url.text, filename)
    return filename

def get_forecast_conditions_icon(parameters):
    return parameters.findall('./conditions-icon/icon-link')

def get_worded_forecast(parameters):
    return parameters.findall('./wordedForecast/text')

def get_forecast_days(forecast):
    return forecast.findall('./time-layout/layout-key[.="' +
        layout_key + '"]/../start-valid-time')

def get_forecast(forecast):
    get_forecast_location(forecast)
    forecast_parameters = forecast.find('./parameters')
    assert forecast_parameters is not None

    icons = get_forecast_conditions_icon(forecast_parameters)
    days = get_forecast_days(forecast)
    words = get_forecast_weather(forecast_parameters)
    maxs = get_forecast_maximum_temperatures(forecast_parameters)
    mins = get_forecast_minimum_temperatures(forecast_parameters)
    maxs_and_mins = [j for i in zip(maxs,mins) for j in i]
    assert len(icons) == len(days) == len(words)

    zipped = zip(icons, days, words, maxs_and_mins)
    # print(list(zipped))

    count = 0
    for i in zipped:
        offset = 100 if count % 2 == 1 else 0
        row = int(count/2)

        print("${{image {} -p {},{}}}".format(get_icon(i[0]), offset,
            120 + row * 100, end=''))

        print('${{goto 200}}{}: {}'.format(i[1].attrib['period-name'],
            i[2].attrib["weather-summary"]), end='')

        if count != 0 and count % 2 == 1:
            print()
            print('${{goto 200}}{}/{}'.format(save, 
                i[3].text if i[3] is not None else 'NA'))
            print('${voffset 9}')
        else:
            save = i[3].text

        count += 1


    # moreWeatherInformation = forecast.find('./moreWeatherInformation')
    # print('get_forecast_forecast', get_worded_forecast(forecast_parameters))

def get_current_location(current_parameters):
    location = current_parameters.find('./location')
    assert location is not None

def get_current_temperature(current_parameters):
    return current_parameters.find('./temperature[@type="apparent"]/value').text or 'NA'

def get_current_humidity(current_parameters):
    return current_parameters.find('./humidity/value').text or 'NA'

def get_current_weather(current_parameters):
    return current_parameters.find('./weather/weather-conditions').attrib["weather-summary"] or 'NA'

def get_current_weather_icon(current_parameters):
    current_icon_link = current_parameters.find('./conditions-icon/icon-link')
    assert current_icon_link is not None
    return get_icon(current_icon_link)

def get_current_wind_speed(current_parameters):
    return current_parameters.find('./wind-speed[@type="sustained"]/value').text or 'NA'

def get_current_wind_direction(current_parameters):
    return current_parameters.find('./direction/value').text or 'NA'

def get_current_pressure(current_parameters):
    return current_parameters.find('./pressure/value').text or 'NA'

def get_current(current):
    get_current_location(current)
    current_parameters = current.find('./parameters')
    assert current_parameters is not None

    print('${{alignc}}{}'.format(
        get_current_weather(current_parameters)))

    print('Temp:${{goto 100}}{}'.format(
        get_current_temperature(current_parameters)), end='')
    print('${{goto 300}}Wind speed:${{goto 410}}{}'.format(
        get_current_wind_speed(current_parameters)), end='')
    print()

    print('RH:${{goto 100}}{}'.format(
        get_current_humidity(current_parameters)), end='')
    print('${{goto 300}}Direction:${{goto 410}}{}'.format(
        get_current_wind_direction(current_parameters)), end='')
    print()

    print('Pressure:${{goto 100}}{}'.format(
        get_current_pressure(current_parameters)), end='')

    print()

    filename = get_current_weather_icon(current_parameters)
    print("${{image {} -p 200,25}}".format(filename))


# https://stackoverflow.com/questions/59067649/assert-true-vs-assert-is-not-none
'''
with open('/home/stevebeaty/src/conky/weather.gov') as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.StringIO(html))
'''
# print('getting forecast', file=sys.stderr)
with urllib.request.urlopen(url) as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.BytesIO(html))

    root = tree.getroot()

    forecast = root.find('./data[@type="forecast"]')
    assert forecast is not None

    fourteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
    if fourteen is None:
        layout_key = 'k-p12h-n13-1'
        thirteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
        assert thirteen is not None

    current = root.find('./data[@type="current observations"]')
    assert current is not None
    get_current(current)

    get_forecast(forecast)
