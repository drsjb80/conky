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

def deal_with_forecast_conditions_icon(parameters):
    icon_links = parameters.findall('./conditions-icon/icon-link')
    assert icon_links is not None
    for url in icon_links:
        get_icon(url)

def deal_with_worded_forecast(parameters):
    worded_forecast = parameters.findall('./wordedForecast/text')
    assert worded_forecast is not None

    for i in worded_forecast:
        # print(i.text)
        pass

def deal_with_forecast_time_layouts(forecast):
    time_layout = forecast.findall('./time-layout/layout-key[.="k-p12h-n13-1"]')
    assert time_layout is not None
    assert len(time_layout) == 1
    for i in time_layout:
        # print(i, i.tag, i.attrib, i.text)
        pass

def deal_with_forecast(forecast):
    deal_with_forecast_location(forecast)
    moreWeatherInformation = forecast.find('./moreWeatherInformation')
    assert moreWeatherInformation is not None
    deal_with_forecast_time_layouts(forecast)

    forecast_parameters = forecast.find('./parameters')
    assert forecast_parameters is not None
    '''
    for child in forecast_parameters:
        print(child.tag, child.attrib, child.text)
    '''
    deal_with_forecast_temperature(forecast_parameters)
    deal_with_forecast_weather(forecast_parameters)
    deal_with_forecast_conditions_icon(forecast_parameters)
    deal_with_worded_forecast(forecast_parameters)

def deal_with_current_location(current_parameters):
    location = current_parameters.find('./location')
    assert location is not None

def deal_with_current_temperature(current_parameters):
    current_temperature = current_parameters.find('./temperature[@type="apparent"]/value') or 'NA'

def deal_with_current_humidity(current_parameters):
    current_humidity = current_parameters.find('./humidity/value') or 'NA'

def deal_with_current_weather(current_parameters):
    current_weather = current_parameters.find('./weather/weather-conditions')
    assert current_weather is not None

def deal_with_current_weather_icon(current_parameters):
    current_icon_link = current_parameters.find('./conditions-icon/icon-link')
    assert current_icon_link is not None
    get_icon(current_icon_link)

def deal_with_current_wind(current_parameters):
    direction = current_parameters.find('./direction/value') or 'NA'
    speed = current_parameters.find('./wind-speed[@type="sustained"]/value') or 'NA'

def deal_with_current_pressure(current_parameters):
    pressure = current_parameters.find('./pressure/value') or 'NA'

def deal_with_current(current):
    deal_with_current_location(current)
    current_parameters = current.find('./parameters')
    assert current_parameters is not None

    deal_with_current_temperature(current_parameters)
    deal_with_current_humidity(current_parameters)
    deal_with_current_weather(current_parameters)
    deal_with_current_weather_icon(current_parameters)
    deal_with_current_wind(current_parameters)
    deal_with_current_pressure(current_parameters)

# https://stackoverflow.com/questions/59067649/assert-true-vs-assert-is-not-none

'''
with urllib.request.urlopen(url) as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.BytesIO(html))
'''
with open('weather.gov') as response:
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
