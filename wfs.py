# -*- coding: utf-8 -*-

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

import json

import datetime

import configparser


class wfs:
    """WFS - Weather Forecast Sources"""

    def __init__(self, sources = []):
        self.sources = sources
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def get_rp5(self):
        logger.info('Receiving data from rp5.ru')

        src_name = 'rp5.ru'

        url = '''http://rp5.ru/Weather_in_Moscow_(Balchug)'''

        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')

        soup = BeautifulSoup(html, 'html5lib')



        fct_html = soup.find(id='forecastTable')

        fct_list = []  # summary forecast list of dicts

        for tr in fct_html.find_all('tr'):
            if tr.td.a:
                n = 0

                # Date
                if tr.td.a.string == 'Local time':

                    logger.debug('Hours parsing and datetime generating')

                    hours = [] # list of hours from page
                    for td in tr.find_all('td'):
                        n += 1
                        if n > 1:
                            hours.append(int(td.string))

                    dates = [] # list of full dates
                    today = datetime.datetime.now().replace(minute = 0, second = 0, microsecond = 0)
                    if today.hour > 21:
                        cur_day = (today + datetime.timedelta(days = 1)).day
                    else:
                        cur_day = today.day
                    for i in range(len(hours)):
                        if i == 0:
                            dates.append(today.replace(day = cur_day, hour = hours[i]))
                        else:
                            if hours[i] < hours[i-1]:
                                #cur_day = cur_day + 1
                                cur_day = (today.replace(day = cur_day) + datetime.timedelta(days = 1)).day

                                dates.append(today.replace(day = cur_day, hour = hours[i]))
                            else:
                                dates.append(today.replace(day = cur_day, hour = hours[i]))

                    for i in range(len(dates)):
                        fct_list.append({'datetime':dates[i]})


                # Weather phenomena
                elif tr.td.a.string == 'Weather phenomena':
                    logger.debug('Parse phenomena')
                    phenomena_list = []
                    for td in tr.find_all('td'):
                        n += 1
                        if n > 1 and 'onmouseover' in list(td.div.attrs.keys()) and n % 2 == 0:
                            phenomena_list.append(td.div.attrs['onmouseover'][17:-13])
                    for i in range(len(fct_list)):
                        fct_list[i]['phenomena'] = phenomena_list[i]


                # Temperature
                elif tr.td.a.string == 'Temperature':
                    logger.debug('Parse temp')
                    temp_list = []
                    for td in tr.find_all('td'):
                        n += 1
                        if n > 1:
                            temp_list.append(td.find(None, {'class' :'t_0'}).get_text())
                    for i in range(len(fct_list)):
                        fct_list[i]['temperature'] = temp_list[i]

                # Feels
                elif tr.td.a.string == 'Feels like':
                    logger.debug('Parse feels')
                    feels_list = []
                    for td in tr.find_all('td'):
                        n += 1
                        k = 0
                        if n > 1 and td.find(None, {'class':'t_0'}):
                            feels_list.append(td.find(None, {'class':'t_0'}).get_text())
                            k += 1
                        elif n > 1:
                            k += 1
                            feels_list.append(temp_list[k])

                    for i in range(len(fct_list)):
                        fct_list[i]['feels_like'] = feels_list[i]

                # Wind
                elif 't_wind_velocity' in list(tr.td.a.attrs.values()):
                    logger.debug('Parse wind')
                    wind_list = []
                    for td in tr.find_all('td'):
                        n += 1
                        if n > 1 and td.find(None, {'class':'wv_0'}):
                            wind_list.append(td.find(None, {'class':'wv_0'}).get_text())
                        elif n > 1:
                            wind_list.append(0)
                    for i in range(len(fct_list)):
                        fct_list[i]['wind'] = wind_list[i]
                else:
                    pass

        for i in range(len(fct_list)):
            fct_list[i]['src_name'] = src_name

        logger.info('Parsing RP5 finished')
        return fct_list




    def get_owm(self):
        '''Get forecast from OpenWeatherMap.org'''
        logger.info('Receiving data from OpenWeatherMap.org')

        src_name = 'OpenWeatherMap.org'

        url = '''http://api.openweathermap.org/data/2.5/forecast?id=524901&mode=json&appid=%s&units=metric''' % self.config['SOURCES']['owm_key']

        response = urllib.request.urlopen(url)
        jsn = response.read().decode('utf-8')

        fct_list = []  # summary forecast list of dicts

        j = json.loads(jsn)
        for i in j['list']:

            l = {}

            dt = datetime.datetime.strptime(i['dt_txt'],'%Y-%m-%d %H:%M:%S')
            phenomena = i['weather'][0]['main']
            temperature = float(i['main']['temp'])
            pressure = float(i['main']['pressure'])
            humidity = int(i['main']['humidity'])
            wind = float(i['wind']['speed'])

            l['datetime'] = dt
            l['phenomena'] = phenomena
            l['temperature'] = temperature
            l['pressure'] = pressure
            l['humidity'] = humidity
            l['wind'] = wind
            l['src_name'] = src_name

            fct_list.append(l)

        logger.info('Parsing OpenWeatherMap.org finished')
        return fct_list


    def _get_wu(self):
        '''[not working] Weather Underground'''
        logger.info('Receiving data from Weather Underground')
        url = '''http://api.wunderground.com/api/%s/forecast10day/q/Russia/Moscow.xml''' % self.config['SOURCES']['wu_key']

        response = urllib.request.urlopen(url)
        xml = response.read().decode('utf-8')

        soup = BeautifulSoup(xml, 'html5lib')

    def _get_theweather_com(self):
        logger.info('[not working] Receiving data from TheWeather.com')
        url = '''http://api.theweather.com/index.php?api_lang=eu&localidad=13564&affiliate_id=%s''' % self.config['SOURCES']['tw_key']

        response = urllib.request.urlopen(url)
        xml = response.read().decode('utf-8')

        soup = BeautifulSoup(xml, 'html5lib')


    def get_all_sources(self):
        '''Get data from all working sources'''
        all = []

        try:
            rp5 = self.get_rp5()
        except Exception as e:
            rp5 = []
            logger.error(e)

        try:
            owm = self.get_owm()
        except Exception as e:
            owm = []
            logger.error(e)

        return rp5 + owm

    def send_to_owm(self, params = {}):
        theurl = 'http://openweathermap.org/data/post'
        values = {'temp' : 27.4,
                  'pressure' : 1016,
                  'humidity' : 56,
                  'lat' : 55.8112,
                  'long' : 37.7287,
                  'alt' : 200,
                  'name' : 'dimeteo' }

        data = urllib.parse.urlencode(values)
        data = data.encode('ascii')




        username = 'd.natxa@gmail.com'
        password = 'galka777'
        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, theurl, username, password)
        authhandler = urllib.request.HTTPBasicAuthHandler(passman)
        opener = urllib.request.build_opener(authhandler)
        urllib.request.install_opener(opener)

        req = urllib.request.Request(theurl, data)
        pagehandle = urllib.request.urlopen(req)
        return pagehandle.read()


