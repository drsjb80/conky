# vim: ts=4 sw=4 expandtab

import io
import re
import sys
import os.path
import urllib.request
import xml.etree.ElementTree

url = 'https://forecast.weather.gov/MapClick.php?lat=' + sys.argv[1] + \
    '&lon=' + sys.argv[2] + '&unit=0&lg=english&FcstType=dwml'

layout_key = 'k-p12h-n14-1'

def get_icon(url):
    ''' Retrieve an icon and return the file name where it was saved. '''
    filename = '/tmp/' + re.sub(r'.*/', '', url.text)
    if not os.path.isfile(filename):
        urllib.request.urlretrieve(url.text, filename)
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
        return self.forecast_parameters.findall('./weather[@time-layout="' + layout_key + '"]/weather-conditions')

    def get_forecast_conditions_icon(self):
        ''' Return a list of icons for forecasts. '''
        return self.forecast_parameters.findall('./conditions-icon/icon-link')

    def get_worded_forecast(self):
        ''' Return a list of long words for forecasts. '''
        return self.forecast_parameters.findall('./wordedForecast/text')

    def get_forecast_days(self):
        ''' Return a list of days that the forecasts refer to. '''
        return self.forecast.findall('./time-layout/layout-key[.="' +
            layout_key + '"]/../start-valid-time')

    def get_more_weather_information(self):
        ''' Return a link to where to get more forecast weather information. '''
        return self.forecast.find('./moreWeatherInformation') or 'NA'

    def print_forecast(self, zipped):
        ''' Print out all the forecast information in conky format. '''
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

    def get_forecast(self):
        ''' Gather all the forecast information and print it out. '''
        # get_forecast_location()
        icons = self.get_forecast_conditions_icon()
        days = self.get_forecast_days()
        words = self.get_forecast_weather()
        maxs = self.get_forecast_maximum_temperatures()
        mins = self.get_forecast_minimum_temperatures()
        maxs_and_mins = [j for i in zip(maxs,mins) for j in i]
        if not (len(icons) == len(days) == len(words)):
            print('Error: inconsistent lenghts')

        zipped = zip(icons, days, words, maxs_and_mins)
        # print(list(zipped))
        self.print_forecast(zipped)

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
        return self.current_parameters.find('./temperature[@type="apparent"]/value').text or 'NA'

    def get_current_humidity(self):
        ''' Return the current relative humidity. '''
        return self.current_parameters.find('./humidity/value').text or 'NA'

    def get_current_weather(self):
        ''' Return the short words for the current condition. '''
        return self.current_parameters.find('./weather/weather-conditions').attrib["weather-summary"] or 'NA'

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
        print('${{alignc}}{}'.format(
            self.get_current_weather()))

        print('Temp:${{goto 100}}{}'.format(
            self.get_current_temperature()), end='')
        print('${{goto 300}}Wind speed:${{goto 410}}{}'.format(
            self.get_current_wind_speed()), end='')
        print()

        print('RH:${{goto 100}}{}'.format(
            self.get_current_humidity()), end='')
        print('${{goto 300}}Direction:${{goto 410}}{}'.format(
            self.get_current_wind_direction()), end='')
        print()

        print('Pressure:${{goto 100}}{}'.format(
            self.get_current_pressure()), end='')

        print()

        filename = self.get_current_weather_icon()
        print("${{image {} -p 200,25}}".format(filename))


# https://stackoverflow.com/questions/59067649/assert-true-vs-assert-is-not-none
'''
with open('/Users/stevebeaty/src/conky/weather.gov') as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.StringIO(html))
'''
# print('getting forecast', file=sys.stderr)

with urllib.request.urlopen(url) as response:
    html = response.read()
    tree = xml.etree.ElementTree.parse(io.BytesIO(html))

    root = tree.getroot()

    forecast = root.find('./data[@type="forecast"]')
    if forecast is None:
        print('No forecast found')

    fourteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
    if fourteen is None:
        layout_key = 'k-p12h-n13-1'
        thirteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
        if thirteen is None:
            print('No time layout found')
            sys.exit(1)

    current = root.find('./data[@type="current observations"]')
    if current is None:
        print('Error: no current conditions found')
    else:
        Current(current).get_current()

    Forecast(forecast).get_forecast()
