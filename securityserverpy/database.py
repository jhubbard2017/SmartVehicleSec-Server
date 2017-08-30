# -*- coding: utf-8 -*-
#
# utility class connecting and controlling postgres database
#

import psycopg2
from configparser import ConfigParser

from securityserver import _logger

class Database(object):
    """module to manage database connections and calls"""

    _CONFIG_PATH = 'database/database.ini'

    def __init__(self):
        self.cursor = None
        self.connection = None
        self.tables = ['mdevices', 'rdevices', 'connections', 'securityconfig', 'contacts', 'logs']

        params = self._get_database_info(Databases._CONFIG_PATH)
        try:
            # Connect to database and establish cursor for communication
            self.connection = psycopg2.connect(**params)
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.DatabaseError) as error:
            _logger.debug('Could not set up database: [{0}]'.format(error))

    def _get_database_info(self, filename, section='postgresql'):
        """retrieves database info from file and returns it

        args:
            filename: str
            section: str

        returns:
            dict
        """
        parser = ConfigParser()
        parser.read(filename)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            _logger.debug('Section {0} not found in the {1} file'.format(section, filename))
            return None

        return db

    def _commit_sql(self, sql, values):
        """inserts data into specified database

        args:
            database: str
            command: str
            values: ()

        returns:
            bool
        """
        success = True
        if not self.cursor:
            _logger.debug('Cursor object not set for database')
            return not success
        if not self.connection:
            _logger.debug('Connection object not set for database')
            return not success
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.debug('Database error: [{0}]'.format(error))
            return not success

        return success

    def _fetch_all_data(self):
        """fetches all data from previous query sql

        returns:
            ()
        """
        success = True
        if not self.cursor:
            _logger.debug('Cursor object not set for database')
            return not success
        try:
            data = self.cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.debug('Database error: [{0}]'.format(error))
            return not success

        return success, data

    def _fetch_one_data(self):
        """fetches a single row of the resulting data set from the previous query sql

        returns:
            bool, ()
        """
        success = True
        if not self.cursor:
            _logger.debug('Cursor object not set for database')
            return not success

        try:
            data = self.cursor.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.debug('Database error: [{0}]'.format(error))
            return not success

        return success, data

    def _fetch_many_data(self, count):
        """fetches a certain number of data from the resulting set

        args:
            count: int
        returns:
            []
        """
        success = True
        if not self.cursor:
            _logger.debug('Cursor object not set for database')
            return not success

        try:
            data = self.cursor.fetchmany(count)
        except (Exception, psycopg2.DatabaseError) as error:
            _logger.debug('Database error: [{0}]'.format(error))
            return not success

        return success, data

    def add_mobile_device(self, mac_address, name):
        sql = 'INSERT INTO mdevices(mac_address, name) VALUES(%s, %s);'
        values = (mac_address, name)
        return self._commit_sql(sql, values)

    def remove_mobile_device(self, mac_address):
        sql = 'DELETE FROM mdevices WHERE mac_address = %s'
        values = (mac_address,)
        return self._commit_sql(sql, values)

    def update_mobile_device(self, mac_address, new_name):
        sql = 'UPDATE mdevices SET name = %s WHERE mac_address = %s'
        values = (new_name, mac_address)
        return self._commit_sql(sql, values)

    def add_raspberry_pi_device(self, md_mac_address, mac_address):
        sql = 'INSERT INTO rdevices(md_mac_address, mac_address) VALUES(%s, %s);'
        values = (md_mac_address, rp_mac_address)
        return self._commit_sql(sql, values)

    def remove_raspberry_pi_device(self, mac_address):
        sql = 'DELETE FROM rdevices WHERE mac_address = %s'
        values = (mac_address,)
        return self._commit_sql(sql, values)

    def get_raspberry_pi_device(self, md_mac_address):
        sql = 'SELECT rd_mac_address from rdevices WHERE md_mac_address = %s'
        values = (md_mac_address,)
        self._commit_sql(sql, values)
        success, data = self._fetch_one_data()
        if not success:
            return None
        return data[0]

    def add_raspberry_pi_connection(self, mac_address, ip_address, port):
        sql = 'INSERT INTO connections(mac_address, ip_address, port) VALUES(%s, %s, %s);'
        values = (mac_address, ip_address, port)
        return self._commit_sql(sql, values)

    def update_raspberry_pi_connection(self, mac_address, ip_address=None, port=None):
        all_success = True
        if ip_address:
            sql = 'UPDATE connections SET ip_address = %s WHERE mac_adress = %s;'
            values = (ip_address, mac_address)
            all_success = all_success and self._commit_sql(sql, values)
        if port:
            sql = 'UPDATE connections SET port = %s WHERE mac_adress = %s;'
            values = (port, mac_address)
            all_success = all_success and self._commit_sql(sql, values)

        return all_success

    def get_raspberry_pi_connection(self, rd_mac_address):
        sql = 'SELECT ip_address, port FROM connections WHERE rd_mac_address = %s'
        values = (rd_mac_address,)
        self._commit_sql(sql, values)
        success, data = self._fetch_one_data()
        if not success or not data:
            return None, None
        ip_address = data[0]
        port = data[1]
        return ip_address, port

    def remove_raspberry_pi_connection(self, mac_address):
        sql = 'DELETE FROM connections WHERE mac_address = %s'
        values = (mac_address,)
        return self._commit_sql(sql, values)

    def add_contact(self, rd_mac_address, name, email, phone):
        sql = 'INSERT INTO contacts(mac_address, name, email, phone) VALUES(%s, %s, %s, %s);'
        values = (rd_mac_address, name, email, phone)
        return self._commit_sql(sql, values)

    def update_contact(self, rd_mac_address, name, email=None, phone=None):
        all_success = True
        if email:
            sql = 'UPDATE contacts SET email = %s WHERE name = %s;'
            values = (email, name)
            all_success = all_success and self._commit_sql(sql, values)
        if phone:
            sql = 'UPDATE contacts SET phone = %s WHERE name = %s;'
            values = (phone, name)
            all_success = all_success and self._commit_sql(sql, values)

        return all_success

    def get_contacts(self, rd_mac_address):
        sql = 'SELECT name, email FROM contacts WHERE rd_mac_address = %s'
        values = (rd_mac_address,)
        self._commit_sql(sql, values)
        success, data = self._fetch_all_data()
        if not success:
            return None
        return [{'name': contact[0], 'email': contact[1]} for contact in data]

    def add_log(self, rd_mac_address, info, date, time, type):
        sql = 'INSERT INTO logs(mac_address, info, date, time, type) VALUES(%s, %s, %s, %s, %s);'
        values = (rd_mac_address, info, date, time, type)
        return self._commit_sql(sql, values)

    def get_logs(self, rd_mac_address, type):
        sql = 'SELECT info, date, time FROM logs WHERE mac_address = %s AND type = %s'
        values = (rd_mac_address, type)
        self._commit_sql(sql, values)
        success, data = self._fetch_all_data()
        if not success:
            return None
        return [{'info': log[0], 'date': log[1], 'time': log[2]} for log in data]

    def remove_log(self):
        pass

    def add_security_config(self, rd_mac_address):
        sql = 'INSERT INTO securityconfig(system_armed, system_breached) VALUES(%s, %s);'
        values = (False, False)
        return self._commit_sql(sql, values)

    def update_security_config(self, rd_mac_address, system_armed=False, system_breached=False):
        all_success = True
        sql = 'UPDATE securityconfig SET system_armed = %s WHERE mac_address = %s'
        values = (system_armed, rd_mac_address)
        all_success = all_success and self._commit_sql(sql, values)

        sql = 'UPDATE securityconfig SET system_breached = %s WHERE mac_address = %s'
        values = (system_breached, rd_mac_address)
        all_success = all_success and self._commit_sql(sql, values)
        return all_success

    def remove_security_config(self):
        pass

    def get_security_config(self, rd_mac_address):
        sql = 'SELECT system_armed, system_breached FROM securityconfig WHERE mac_address = %s'
        values = (rd_mac_address,)
        self._commit_sql(sql, values)
        success, data = self._fetch_one_data()
        if not success:
            return None
        return {'system_armed': data[0], 'system_breached': data[1]}

    def clear_all_tables(self):
        for table in self.tables:
            sql = 'TRUNCATE TABLE {0}'.format(table)
            values = ()
            self._commit_sql(sql, values)
