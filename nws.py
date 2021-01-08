# vim: ts=4 sw=4 expandtab

import io
import re
import sys
import os.path
import urllib.request
import xml.etree.ElementTree

url = 'https://forecast.weather.gov/MapClick.php?lat=39.54&lon=-104.91&unit=0&lg=english&FcstType=dwml'

layout_key = 'k-p12h-n14-1'

def get_icon(url):
    filename = '/tmp/' + re.sub(r'.*/', '', url.text)
    if not os.path.isfile(filename):
        urllib.request.urlretrieve(url.text, filename)
    return filename

class Forecast:
    def __init__(self, forecast):
        self.forecast = forecast
        self.forecast_parameters = self.forecast.find('./parameters')

    def get_forecast_location(self):
        return self.forecast.find('./location').find('./point') or 'NA'

    def get_forecast_maximum_temperatures(self):
        return self.forecast_parameters.findall('./temperature[@type="maximum"]/value')

    def get_forecast_minimum_temperatures(self):
        return self.forecast_parameters.findall('./temperature[@type="minimum"]/value')

    def get_forecast_weather(self):
        return self.forecast_parameters.findall('./weather[@time-layout="' + layout_key + '"]/weather-conditions')

    def get_forecast_conditions_icon(self):
        return self.forecast_parameters.findall('./conditions-icon/icon-link')

    def get_worded_forecast(self):
        return self.forecast_parameters.findall('./wordedForecast/text')

    def get_forecast_days(self):
        return self.forecast.findall('./time-layout/layout-key[.="' +
            layout_key + '"]/../start-valid-time')

    def get_moreWeatherInformation(self):
        return self.forecast.find('./moreWeatherInformation') or 'NA'

    def print_forecast(self, zipped):
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
        # get_forecast_location()
        icons = self.get_forecast_conditions_icon()
        days = self.get_forecast_days()
        words = self.get_forecast_weather()
        maxs = self.get_forecast_maximum_temperatures()
        mins = self.get_forecast_minimum_temperatures()
        maxs_and_mins = [j for i in zip(maxs,mins) for j in i]
        assert len(icons) == len(days) == len(words)

        zipped = zip(icons, days, words, maxs_and_mins)
        # print(list(zipped))
        self.print_forecast(zipped)

class Current:
    def __init__(self, current):
        self.current = current
        self.current_parameters = self.current.find('./parameters')

    def get_current_location(self):
        return self.current_parameters.find('./location') or 'NA'

    def get_current_temperature(self):
        return self.current_parameters.find('./temperature[@type="apparent"]/value').text or 'NA'

    def get_current_humidity(self):
        return self.current_parameters.find('./humidity/value').text or 'NA'

    def get_current_weather(self):
        return self.current_parameters.find('./weather/weather-conditions').attrib["weather-summary"] or 'NA'

    def get_current_weather_icon(self):
        current_icon_link = self.current_parameters.find('./conditions-icon/icon-link')
        assert current_icon_link is not None
        return get_icon(current_icon_link)

    def get_current_wind_speed(self):
        return self.current_parameters.find('./wind-speed[@type="sustained"]/value').text or 'NA'

    def get_current_wind_direction(self):
        return self.current_parameters.find('./direction/value').text or 'NA'

    def get_current_pressure(self):
        return self.current_parameters.find('./pressure/value').text or 'NA'

    def get_current(self):
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
    assert forecast is not None

    fourteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
    if fourteen is None:
        layout_key = 'k-p12h-n13-1'
        thirteen = forecast.find('./time-layout/layout-key[.="' + layout_key + '"]')
        assert thirteen is not None

    current = root.find('./data[@type="current observations"]')
    assert current is not None
    Current(current).get_current()

    Forecast(forecast).get_forecast()
