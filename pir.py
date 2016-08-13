# -*- coding: utf-8 -*-

# Passive Infrared Sensor module

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

import RPi.GPIO as GPIO

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

import os, time, subprocess

#os.environ['DISPLAY'] = ":0"

GPIO.setmode(GPIO.BCM)
PIR_PIN = int(config['GPIO']['PIR_pin'])
GPIO.setup(PIR_PIN, GPIO.IN)

def screensaver():
    subprocess.call('DISPLAY=:0 xset dpms force off', shell=True)
    displayison = False
    maxidle = int(config['GENERAL']['display_idle'])*60 # seconds
    lastsignaled = 0
    while True:
        now = time.time()
        if GPIO.input(PIR_PIN):
                if not displayison:
                    logger.debug('Display turning ON')
                    subprocess.call('DISPLAY=:0 xset dpms force on', shell=True)
                    displayison = True
                lastsignaled = now
        else:
            if now-lastsignaled > maxidle:
                if displayison:
                        logger.debug('Display turning OFF')
                        subprocess.call('DISPLAY=:0 xset dpms force off', shell=True)
                        displayison = False
        time.sleep(1)






