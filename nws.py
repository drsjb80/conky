# vim: ts=4 sw=4 expandtab

import io
import re
import os.path
import urllib.request
import xml.etree.ElementTree

url = 'https://forecast.weather.gov/MapClick.php?lat=39.54&lon=-104.91&unit=0&lg=english&FcstType=dwml'

def deal_with_forecast_location(forecast):
    location = forecast.find('./location')
    assert location is not None
    point = location.find('./point')
    assert point is not None

def deal_with_forecast_temperature(parameters):
    maximum = parameters.find('./temperature[@type="maximum"]')
    assert maximum is not None
    minimum = parameters.find('./temperature[@type="minimum"]')
    assert minimum is not None

def deal_with_forecast_weather(parameters):
    weather = parameters.find('./weather')
    assert weather is not None
    for i in weather.findall('weather-conditions'):
        # print(i.attrib['weather-summary'])
        pass

def get_icon(url):
    filename = '/tmp/' + re.sub(r'.*/', '', url.text)
    if not os.path.isfile(filename):
        urllib.request.urlretrieve(url.text, filename)
    return filename

def deal_with_forecast_conditions_icon(parameters):
    icon_links = parameters.findall('./conditions-icon/icon-link')
    assert icon_links is not None
    for url in icon_links:
        get_icon(url)

    count = 0
    for day in icon_links[2::2]:
        filename = '/tmp/' + re.sub(r'.*/', '', day.text)
        print('${{image {} -p {},100}}'.format(filename, count*100))
        count += 1

    count = 0
    for night in icon_links[1::2]:
        filename = '/tmp/' + re.sub(r'.*/', '', night.text)
        print('${{image {} -p {},200}}'.format(filename, count*100))
        count += 1

def deal_with_worded_forecast(parameters):
    worded_forecast = parameters.findall('./wordedForecast/text')
    assert worded_forecast is not None

    for i in worded_forecast:
        # print(i.text)
        pass

def deal_with_forecast_day_time_layout(forecast):
    time_layout = forecast.findall('./time-layout/layout-key[.="k-p24h-n7-1"]/../start-valid-time')
    assert time_layout is not None
    count = 0
    for i in time_layout[1:]:
        print('${{goto {}}}'.format(count * 100), end='')
        print(i.attrib['period-name'][:3], end='')
        count += 1

def deal_with_forecast_night_time_layout(forecast):
    time_layout = forecast.findall('./time-layout/layout-key[.="k-p24h-n6-2"]/../start-valid-time')
    assert time_layout is not None
    count = 0
    for i in time_layout[1:]:
        print('${{goto {}}}'.format(count * 100), end='')
        print(i.attrib['period-name'].split(' ')[0][:3], end='')
        count += 1

def deal_with_forecast(forecast):
    deal_with_forecast_location(forecast)
    moreWeatherInformation = forecast.find('./moreWeatherInformation')
    assert moreWeatherInformation is not None

    forecast_parameters = forecast.find('./parameters')
    assert forecast_parameters is not None
    '''
    for child in forecast_parameters:
        print(child.tag, child.attrib, child.text)
    '''
    deal_with_forecast_temperature(forecast_parameters)
    deal_with_forecast_weather(forecast_parameters)
    deal_with_forecast_day_time_layout(forecast)
    print()
    deal_with_forecast_conditions_icon(forecast_parameters)
    # deal_with_forecast_night_time_layout(forecast)
    deal_with_worded_forecast(forecast_parameters)

def deal_with_current_location(current_parameters):
    location = current_parameters.find('./location')
    assert location is not None

def deal_with_current_temperature(current_parameters):
    current_temperature = current_parameters.find('./temperature[@type="apparent"]/value').text or 'NA'
    print(current_temperature, end='')

def deal_with_current_humidity(current_parameters):
    current_humidity = current_parameters.find('./humidity/value').text or 'NA'
    print(current_humidity, end='')

def deal_with_current_weather(current_parameters):
    current_weather = current_parameters.find('./weather/weather-conditions').attrib["weather-summary"] or 'NA'
    print(current_weather, end='')

def deal_with_current_weather_icon(current_parameters):
    current_icon_link = current_parameters.find('./conditions-icon/icon-link')
    assert current_icon_link is not None
    filename = get_icon(current_icon_link)
    print("${image ", filename, " -p 700,100}")

def deal_with_current_wind_speed(current_parameters):
    speed = current_parameters.find('./wind-speed[@type="sustained"]/value').text or 'NA'
    print(speed, end='')

def deal_with_current_wind_direction(current_parameters):
    direction = current_parameters.find('./direction/value') or 'NA'
    print(direction, end='')

def deal_with_current_pressure(current_parameters):
    pressure = current_parameters.find('./pressure/value').text or 'NA'

def deal_with_current(current):
    deal_with_current_location(current)
    current_parameters = current.find('./parameters')
    assert current_parameters is not None

    print(' ' * 20, end='')
    deal_with_current_temperature(current_parameters)
    print(' ' * 20, end='')
    deal_with_current_weather(current_parameters)
    print(' ' * 20, end='')
    deal_with_current_wind_speed(current_parameters)
    print()
    print(' ' * 20, end='')
    deal_with_current_humidity(current_parameters)
    print(' ' * 40, end='')
    deal_with_current_wind_direction(current_parameters)
    deal_with_current_weather_icon(current_parameters)
    print()
    deal_with_current_pressure(current_parameters)

# vim: ts=4 sw=4

# https://stackoverflow.com/questions/59067649/assert-true-vs-assert-is-not-none

'''
with urllib.request.urlopen(url) as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.BytesIO(html))
'''
with open('/home/beaty/src/conky/weather.gov') as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.StringIO(html))
    root = tree.getroot()
    '''
    for child in root:
        print(child.tag, child.attrib)
    '''
    # these have an __len__() that might be non-zero
    forecast = root.find('./data[@type="forecast"]')
    assert forecast is not None
    deal_with_forecast(forecast)

    current = root.find('./data[@type="current observations"]')
    assert current is not None
    deal_with_current(current)
