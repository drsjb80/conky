# vim: ts=4 sw=4 expandtab

import io
import re
import sys
import os
import urllib.request
import xml.etree.ElementTree
import logging

logging.basicConfig(level=logging.WARNING)

LAYOUT_KEY = ''

def print_forecast(zipped):
    ''' Print out all the forecast information in conky format. '''
    count = 0
    for i in zipped:
        offset = 100 if count % 2 == 1 else 0
        row = int(count/2)

        print("${{image {} -p {},{}}}".format(get_icon(i[0]), offset, \
            120 + row * 100, end=''))
        print('${{goto 200}}{}: {}'.format(i[1].attrib['period-name'], \
            i[2].attrib["weather-summary"]), end='')

        if count != 0 and count % 2 == 1:
            print()
            print('${{goto 200}}{}/{}'.format(save, i[3].text if i[3] is not None else 'NA'))
            print('${voffset 9}')
        else:
            save = i[3].text

        count += 1

def get_icon(url):
    ''' Retrieve an icon and return the file name where it was saved. '''
    filename = '/tmp/NWS/' + re.sub(r'.*/', '', url.text)
    if not os.path.isfile(filename):
        try:
            urllib.request.urlretrieve(url.text, filename)
        except ValueError as ve:
            print(ve)
            print(url)
            print(filename)
    return filename

class Forecast:
    ''' A class to collect and display the NWS forecast information. '''
    def __init__(self, forecast):
        self.forecast = forecast
        self.forecast_parameters = self.forecast.find('./parameters')

    def get_forecast_location(self):
        ''' Return where the forecast is actually for. '''
        return self.forecast.find('./location').find('./point') or 'NA'

    def get_forecast_maximum_temperatures(self):
        ''' Return a list of maximum forecasted temperatures. '''
        return self.forecast_parameters.findall('./temperature[@type="maximum"]/value')

    def get_forecast_minimum_temperatures(self):
        ''' Return a list of minimum forecasted temperatures. '''
        return self.forecast_parameters.findall('./temperature[@type="minimum"]/value')

    def get_forecast_weather(self):
        ''' Return a list of words for forecasts. '''
        return self.forecast_parameters.findall('./weather[@time-layout="' + \
            LAYOUT_KEY + '"]/weather-conditions')

    def get_forecast_conditions_icon(self):
        ''' Return a list of icons for forecasts. '''
        return self.forecast_parameters.findall('./conditions-icon/icon-link')

    def get_worded_forecast(self):
        ''' Return a list of long words for forecasts. '''
        return self.forecast_parameters.findall('./wordedForecast/text')

    def get_forecast_days(self):
        ''' Return a list of days that the forecasts refer to. '''
        return self.forecast.findall('./time-layout/layout-key[.="' + \
            LAYOUT_KEY + '"]/../start-valid-time')

    def get_more_weather_information(self):
        ''' Return a link to where to get more forecast weather information. '''
        return self.forecast.find('./moreWeatherInformation') or 'NA'


    def get_forecast(self):
        ''' Gather all the forecast information and print it out. '''
        # get_forecast_location()
        icons = self.get_forecast_conditions_icon()
        days = self.get_forecast_days()
        words = self.get_forecast_weather()
        maxs = self.get_forecast_maximum_temperatures()
        mins = self.get_forecast_minimum_temperatures()
        maxs_and_mins = [j for i in zip(maxs, mins) for j in i]
        if not (len(icons) == len(days) == len(words)):
            print('Error: inconsistent lenghts')

        zipped = zip(icons, days, words, maxs_and_mins)
        print_forecast(zipped)

class Current:
    ''' A class to collect and display the NWS current information. '''
    def __init__(self, current):
        self.current = current
        self.current_parameters = self.current.find('./parameters')

    def get_current_location(self):
        ''' Return information about the location requested. '''
        return self.current_parameters.find('./location') or 'NA'

    def get_current_temperature(self):
        ''' Return the current temperature. '''
        return self.current_parameters.find \
            ('./temperature[@type="apparent"]/value').text or 'NA'

    def get_current_humidity(self):
        ''' Return the current relative humidity. '''
        return self.current_parameters.find('./humidity/value').text or 'NA'

    def get_current_weather(self):
        ''' Return the short words for the current condition. '''
        return self.current_parameters.find \
            ('./weather/weather-conditions').attrib["weather-summary"] or 'NA'

    def get_current_weather_icon(self):
        ''' Return the file name for the current icon. '''
        current_icon_link = self.current_parameters.find('./conditions-icon/icon-link')
        if current_icon_link is None:
            print('Error: icon not found')
            return None
        return get_icon(current_icon_link)

    def get_current_wind_speed(self):
        ''' Return the current wind speed. '''
        return self.current_parameters.find('./wind-speed[@type="sustained"]/value').text or 'NA'

    def get_current_wind_direction(self):
        ''' Return the current wind direction in degrees. '''
        return self.current_parameters.find('./direction/value').text or 'NA'

    def get_current_pressure(self):
        ''' Return the current barometric pressure. '''
        return self.current_parameters.find('./pressure/value').text or 'NA'

    def get_current(self):
        ''' Gather all the current information and print it out in conky format. '''
        print(self.get_current_weather(), end='')
        print('${{goto 300}}Wind speed:${{goto 410}}{}'.format(self.get_current_wind_speed()))

        print('Temp:${{goto 100}}{}'.format(self.get_current_temperature()), end='')
        print('${{goto 300}}Direction:${{goto 410}}{}'.format(self.get_current_wind_direction()))

        print('RH:${{goto 100}}{}'.format(self.get_current_humidity()), end='')
        print('${{goto 300}}Pressure:${{goto 410}}{}'.format(self.get_current_pressure()))

        filename = self.get_current_weather_icon()
        print("${{image {} -p 200,0}}".format(filename))


# https://stackoverflow.com/questions/59067649/assert-true-vs-assert-is-not-none
# print('getting forecast', file=sys.stderr)

'''
    with open('/home/beaty/src/conky/MapClick.xml') as response:
        HTML = response.read()
        TREE = xml.etree.ElementTree.parse(io.StringIO(HTML))
'''

SOURCE_URL = 'https://forecast.weather.gov/MapClick.php?lat=' + sys.argv[1] + \
    '&lon=' + sys.argv[2] + '&unit=0&lg=english&FcstType=dwml'
logging.debug(SOURCE_URL)

try:
    try:
        os.mkdir("/tmp/NWS")
    except FileExistsError as FEE:
        logging.debug(FEE)

    with urllib.request.urlopen(SOURCE_URL) as response:
        HTML = response.read()
        TREE = xml.etree.ElementTree.parse(io.BytesIO(HTML))

        ROOT = TREE.getroot()

        FORECAST = ROOT.find('./data[@type="forecast"]')
        if not FORECAST:
            print('No forecast found')
            sys.exit(1)

        f = FORECAST.findall('./time-layout/layout-key')
        for eff in f:
            for layout in range(13, 16):
                l = 'k-p12h-n' + str(layout) + '-1'
                if eff.text == l:
                    LAYOUT_KEY = l
                    break
            if LAYOUT_KEY != '':
                break

        if not LAYOUT_KEY:
            print('No layout found')
            sys.exit(1)

        CURRENT = ROOT.find('./data[@type="current observations"]')
        if not CURRENT:
            print('Error: no current conditions found')
        else:
            Current(CURRENT).get_current()

        Forecast(FORECAST).get_forecast()
except Exception as err:
    print(err)
