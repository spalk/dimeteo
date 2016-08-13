import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

# dimeteo modules
import gui, wfs, db, timer, sensors, pir

from threading import Thread


def main():
    # Get forecasts and save to DB
    def get_forecasts():
        data = wfs.wfs().get_all_sources()
        dbase = db.db()
        dbase.insert_wfs_data(data)
        dbase.close_connection()

    # Read data from sensors and save to DB
    def read_sensors():
        data = sensors.sensors().read_all()
        dbase = db.db()
        dbase.insert_sensor_data(data)
        dbase.close_connection()

    # Screensaver
    scr = Thread(target = pir.screensaver)
    scr.daemon = True
    scr.start()

    ##test
    ##get_forecasts()
    ##read_sensors()


    # get data from forecasts each hour
    repeat_get_forecasts = timer.timer(3600, get_forecasts)
    repeat_get_forecasts.start()

    # get data from sensors each minute
    repreat_read_sensors = timer.timer(60, read_sensors)
    repreat_read_sensors.start()

    # Send sensor data to openweathermap.com
    #response = wfs.wfs().send_to_owm()
    #print (response)

    # Interface
    root = gui.Interface()
    root.mainloop()



if __name__ == '__main__':
    main()






# 'application' code
#logger.debug('debug message')
#logger.info('info message')
#logger.warn('warn message')
#logger.error('error message')
#logger.critical('critical message')



