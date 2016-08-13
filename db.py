# -*- coding: utf-8 -*-

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import sqlite3, collections, datetime

class db:

    def __init__(self):
        logger.info('Connection to DB')
        self.connection = sqlite3.connect('dimeteo.db')
        self.cur = self.connection.cursor()

        # Create main tables, if they doesn't exist:
        # "forecasts", "sensors"
        if not self.check_table_exist('forecasts'):
            logger.info('Table forecasts not found. Creating...')
            query = """CREATE TABLE forecasts(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    src_name VARCHAR(50),
                    datetime DATETIME,
                    temperature FLOAT,
                    pressure FLOAT,
                    humidity FLOAT,
                    phenomena VARCHAR(200),
                    feels_like FLOAT,
                    wind FLOAT
                    )"""
            self.cur.execute(query)
            self.connection.commit()

        if not self.check_table_exist('sensors'):
            logger.info('Table sensors not found. Creating...')
            query = """CREATE TABLE sensors(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    sensor_name VARCHAR(50),
                    datetime DATETIME,
                    value FLOAT
                    )"""
            self.cur.execute(query)
            self.connection.commit()

    def insert_wfs_data(self, data):
        """ Insertin or Updating data from weather forcast sources """
        logger.info('Inserting data from WFS to DB')

        # Get summary list of parameters of all sources
        source_params_all = []
        for dic in data:
            for key in dic.keys():
                if key not in source_params_all:
                    source_params_all.append(key)

        # Preparing instert/update tuples. For empty parameter - set NULL
        list_of_tuples = []
        for dic in data:

            # Add missing parameters with value NULL
            for param in source_params_all:
                if param not in dic.keys():
                    dic[param] = 'NULL'

            tupl = (dic['src_name'],
                    dic['datetime'],
                    dic['temperature'],
                    dic['pressure'],
                    dic['humidity'],
                    dic['phenomena'],
                    dic['feels_like'],
                    dic['wind']
                )

            list_of_tuples.append(tupl)

        # Generate insert or update query
        count_insert = 0
        count_update = 0
        for t in list_of_tuples:
            if self.check_row_exist('forecasts', {'src_name':t[0], 'datetime':t[1]}):
                count_update += 1
                tup_for_upd = t[2:] + t[:2] # change order a little
                query = """UPDATE forecasts SET temperature = ?, \
                                        pressure = ?, humidity = ?, \
                                        phenomena = ?, feels_like = ?, \
                                        wind = ?  WHERE src_name = ? \
                                        AND datetime = ? """
                self.cur.execute(query, tup_for_upd)

            else:
                count_insert += 1
                query = """INSERT INTO forecasts (src_name, datetime, temperature, \
                                        pressure, humidity, phenomena, \
                                        feels_like, wind) values \
                                         (?, ?, ?, ?, ?, ?, ?, ?)"""
                self.cur.execute(query, t)

            self.connection.commit()

        logger.info('Inserting %s rows complete' % count_insert)
        logger.info('Updating %s complete' % count_update)


    def insert_sensor_data(self, sensor_dic):
        """ Insertin data from sensors """
        logger.info('Inserting data from Sensors to DB')

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Preparing instert tuples
        list_of_tuples = []
        for sensor_name in sensor_dic:
            tupl = (sensor_name,
                    dt,
                    sensor_dic[sensor_name]
                )

            list_of_tuples.append(tupl)

        # Generate insert or update query
        count_insert = 0
        for t in list_of_tuples:
            count_insert += 1
            query = """INSERT INTO sensors (sensor_name, datetime, value) \
                                    values (?, ?, ?)"""
            self.cur.execute(query, t)
            self.connection.commit()

        logger.info('Inserting %s rows complete' % count_insert)


    def check_table_exist(self, tablename):
        """ Check if table exist """
        self.cur.execute(""" SELECT COUNT(*) FROM sqlite_master WHERE  type='table' AND name = ?  """, (tablename, ))
        res = self.cur.fetchone()
        if bool(res[0]):
            return True
        else:
            return False

    def check_row_exist(self, tablename, dictionary):
        """ Check if raw with *dictionary* parameters in *table* exist """

        where_str = ''
        n = 0
        for key in dictionary.keys():
            n += 1
            if n > 1: where_str += ' AND '
            where_str += str(key) + " = '" + str(dictionary[key]) + "'"

        self.cur.execute(" SELECT COUNT(*) FROM %s WHERE  %s " % (tablename, where_str)) # FIX IT
        res = self.cur.fetchone()
        if bool(res[0]):
            return True
        else:
            return False

    def close_connection(self):
        """Close connection"""
        self.connection.close()



class Gui_Data:

    def __init__(self):
        connection = sqlite3.connect('dimeteo.db')
        self.cur = connection.cursor()

    def get_temp_24h(self):
        self.cur.execute("""SELECT *
                            FROM sensors
                            WHERE sensors.datetime >= datetime('now','-1 day')
                            AND
                            sensor_name  = 'temp_DS18B20'
                            ORDER BY datetime(sensors.datetime) ASC""")
        res = self.cur.fetchall()
        data_limit = 200 # depends on graf width in pixels
        n = 1
        if len(res) > data_limit:
            n = int(len(res)/data_limit)
            logger.info('Averaging factor is %s' % n )
        val = []
        koord = []
        count = 0
        local_summ = 0
        for i in res:
            if count != n:
                count += 1
                local_summ += i[3]
            else:
                koord.append(i[2])
                koord.append(local_summ/n)
                val.append(koord)
                koord = []
                local_summ = 0
                count = 0


        data = collections.OrderedDict()
        for i in  val:
            data[datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')] = i[1]
        #ordered_data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))
        return data



# (7, 'temp_DS18B20', '2016-07-23 16:31:11', 33.062)

