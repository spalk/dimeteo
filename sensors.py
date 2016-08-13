# -*- coding: utf-8 -*-


import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import os
import glob
import time

from Adafruit_BME280 import *

class sensors:
    """Get data from sensors"""

    def __init__(self):
        # DS18B20 sensor initialisation
        logger.info('DS18B20 sensor initialisation')
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        # BME280 sensor initialisation
        logger.info('BME280 sensor initialisation')
        self.sensor = BME280(mode=BME280_OSAMPLE_8, address = 0x76)


    # DS18B20 - 1-wire protocol temperature sensor (for outdoor)
    def read_temp_DS18B20_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp_DS18B20(self):
        logger.info('Reading temperature from DS18B20')
        lines = self.read_temp_DS18B20_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_DS18B20_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    # BME280 - I2C protocol temp, pressure and humidity sensor (for indoor)
    def read_temp_BME280(self):
        logger.info('Reading temperature from BME280')
        degrees = self.sensor.read_temperature()
        return degrees

    def read_pressure_BME280(self):
        logger.info('Reading preassre from BME280')
        pascals = self.sensor.read_pressure()
        return pascals

    def read_humid_BME280(self):
        logger.info('Reading humidity from BME280')
        humidity = self.sensor.read_humidity()
        return humidity

    def read_all(self):
        '''Get all data from sensors'''

        s_all = {}

        try:
            val = self.read_temp_DS18B20()
            s_all['temp_DS18B20'] = val
            logger.info('temp_DS18B20 = %s' % val)
        except Exception as e:
            logger.error(e)

        try:
            s_all['temp_BME280'] = self.read_temp_BME280()
        except Exception as e:
            logger.error(e)

        try:
            s_all['pressure_BME280'] = self.read_pressure_BME280()
        except Exception as e:
            logger.error(e)

        try:
            s_all['humid_BME280'] = self.read_humid_BME280()
        except Exception as e:
            logger.error(e)

        return s_all






