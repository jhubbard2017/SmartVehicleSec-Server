# -*- coding: utf-8 -*-
#
# utility class connecting and controlling postgres database
#

import psycopg2
from configparser import ConfigParser
import datetime
import hashlib

from securityserverpy import _logger

class Database(object):
    """module to manage database connections and calls"""

    _CONFIG_PATH = 'securityserverpy/database/database.ini'

    def __init__(self):
        """constructor method"""
        self.cursor = None
        self.connection = None
        self.tables = ['users', 'connections', 'securityconfig', 'contacts', 'logs']

        params = self._get_database_info(Database._CONFIG_PATH)
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

        return data

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

        return data

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

        return data

    def add_user(self, email, password, firstname, lastname, phone, vehicle, system_id):
        """adds user to the database

        args:
            email: str
            password: str
            firstname: str
            lastname: str
            phone: str
            vehicle: str
            system_id: str

        returns:
            bool
        """
        sql = 'INSERT INTO users(email, password, firstname, lastname, phone, vehicle, system_id, logged_in) ' \
              'VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'
        values = (email, password, firstname, lastname, phone, vehicle, system_id, False)
        return self._commit_sql(sql, values)

    def remove_user(self, email):
        """removes user from the database

        args:
            email: str

        returns:
            bool
        """
        sql = 'DELETE FROM users WHERE email = %s;'
        values = (email,)
        return self._commit_sql(sql, values)

    def update_user(self, email, password=None, firstname=None, lastname=None, phone=None, vehicle=None, system_id=None, logged_in=None):
        """updates user in the database

        args:
            email: str
            password: str (default=None)
            firstname: str (default=None)
            lastname: str (default=None)
            phone: str (default=None)
            vehicle: str (default=None)
            system_id: str (default=None)

        returns:
            bool
        """
        all_success = True
        if password:
            sql = 'UPDATE users SET password = %s WHERE email = %s;'
            values = (password, email)
            all_success = all_success and self._commit_sql(sql, values)
        if firstname:
            sql = 'UPDATE users SET firstname = %s WHERE email = %s;'
            values = (firstname, email)
            all_success = all_success and self._commit_sql(sql, values)
        if lastname:
            sql = 'UPDATE users SET lastname = %s WHERE email = %s;'
            values = (lastname, email)
            all_success = all_success and self._commit_sql(sql, values)
        if phone:
            sql = 'UPDATE users SET phone = %s WHERE email = %s;'
            values = (phone, email)
            all_success = all_success and self._commit_sql(sql, values)
        if vehicle:
            sql = 'UPDATE users SET vehicle = %s WHERE email = %s;'
            values = (vehicle, email)
            all_success = all_success and self._commit_sql(sql, values)
        if system_id:
            sql = 'UPDATE users SET system_id = %s WHERE email = %s;'
            values = (system_id, email)
            all_success = all_success and self._commit_sql(sql, values)
        if logged_in != None:
            sql = 'UPDATE users SET logged_in = %s WHERE email = %s;'
            values = (logged_in, email)
            all_success = all_success and self._commit_sql(sql, values)

        return all_success

    def get_user(self, email):
        """get user from database

        args:
            email: str
            password: str

        returns:
            {firstname, lastname, phone, vehicle, system_id, logged_in}
        """
        sql = 'SELECT firstname, lastname, phone, vehicle, system_id, logged_in FROM users WHERE email = %s;'
        values = (email,)
        self._commit_sql(sql, values)
        data = self._fetch_one_data()
        if not data or len(data) == 0:
            return None
        user = {'firstname': data[0], 'lastname': data[1], 'phone': data[2], 'vehicle': data[3], 'system_id': data[4], 'logged_in': data[5]}
        return user

    def verify_user(self, email, password):
        """verify user exist and password is correct

        args:
            email: str
            password: str

        returns:
            bool
        """
        sql = 'SELECT logged_in FROM users WHERE email = %s AND password = %s;'
        values = (email, password)
        self._commit_sql(sql, values)
        data = self._fetch_one_data()
        if not data or len(data) == 0:
            return None
        return {'logged_in': data[0]}

    def get_user_with_system_id(self, system_id):
        """get user from database with system id

        args:
            system_id: str

        returns:
            {firstname, lastname, phone, vehicle, system_id}
        """
        sql = 'SELECT firstname, lastname, phone, vehicle, system_id FROM users WHERE system_id = %s;'
        values = (system_id,)
        self._commit_sql(sql, values)
        data = self._fetch_one_data()
        if not data or len(data) == 0:
            return None
        user = {'firstname': data[0], 'lastname': data[1], 'phone': data[2], 'vehicle': data[3], 'system_id': data[4]}
        return user

    def add_connection(self, system_id, host, port):
        """add connection to database

        args:
            system_id: str
            host: str
            port: str

        returns:
            bool
        """
        sql = 'INSERT INTO connections(system_id, host, port) VALUES(%s, %s, %s);'
        values = (system_id, host, port)
        return self._commit_sql(sql, values)

    def update_connection(self, system_id, host=None, port=None):
        """update connection in database

        args:
            system_id: str
            host: str (default=None)
            port: str (default=None)

        returns:
            bool
        """
        all_success = True
        if host:
            sql = 'UPDATE connections SET host = %s WHERE system_id = %s;'
            values = (host, system_id)
            all_success = all_success and self._commit_sql(sql, values)
        if port:
            sql = 'UPDATE connections SET port = %s WHERE system_id = %s;'
            values = (port, system_id)
            all_success = all_success and self._commit_sql(sql, values)

        return all_success

    def get_connection(self, system_id):
        """get connection from database

        args:
            system_id: str

        returns:
            {host, port}
        """
        sql = 'SELECT host, port FROM connections WHERE system_id = %s;'
        values = (system_id,)
        self._commit_sql(sql, values)
        data = self._fetch_one_data()
        if not data or len(data) == 0:
            return None
        return {'host': data[0], 'port': data[1]}

    def remove_connection(self, system_id):
        """removes connection from database

        args:
            system_id: str

        returns:
            bool
        """
        sql = 'DELETE FROM connections WHERE system_id = %s;'
        values = (system_id,)
        return self._commit_sql(sql, values)

    def add_contact(self, system_id, name, email, phone):
        """add contact to database for user/system

        args:
            system_id: str
            name: str
            email: str
            phone: str

        returns:
            bool
        """
        sql = 'INSERT INTO contacts(system_id, name, email, phone) VALUES(%s, %s, %s, %s);'
        values = (system_id, name, email, phone)
        return self._commit_sql(sql, values)

    def update_contact(self, system_id, name, email=None, phone=None):
        """update contact on database for user/system

        args:
            system_id: str
            name: str
            email: str (Default=None)
            phone: str (Default=None)

        returns:
            bool
        """
        all_success = True
        if email:
            sql = 'UPDATE contacts SET email = %s WHERE name = %s AND system_id = %s;'
            values = (email, name, system_id)
            all_success = all_success and self._commit_sql(sql, values)
        if phone:
            sql = 'UPDATE contacts SET phone = %s WHERE name = %s AND system_id = %s;'
            values = (phone, name, system_id)
            all_success = all_success and self._commit_sql(sql, values)
        return all_success

    def remove_contact(self, system_id, name):
        """remove contact from database for user/system

        args:
            system_id: str
            name: str

        returns:
            bool
        """
        sql = 'DELETE FROM contacts WHERE system_id = %s AND name = %s;'
        values = (system_id, name)
        return self._commit_sql(sql, values)

    def remove_all_contacts(self, system_id):
        """remove all contacts from database for user/system

        args:
            system_id: str

        returns:
            bool
        """
        sql = 'DELETE FROM contacts WHERE system_id = %s;'
        values = (system_id,)
        return self._commit_sql(sql, values)

    def get_contacts(self, system_id):
        """get contacts from database for user/system

        args:
            system_id: str

        returns:
            [{name, email, phone}]
        """
        sql = 'SELECT name, email, phone FROM contacts WHERE system_id = %s;'
        values = (system_id,)
        self._commit_sql(sql, values)
        data = self._fetch_all_data()
        if not data or len(data) == 0:
            return None
        return [{'name': contact[0], 'email': contact[1], 'phone': contact[2]} for contact in data]

    def add_log(self, system_id, info):
        """add log to database for user/system

        args:
            system_id: str
            info: str

        returns:
            bool
        """
        current_date = datetime.datetime.now()
        date = '{:%b %d, %Y}'.format(current_date)
        time = '{:%-I:%M %p}'.format(current_date)
        sql = 'INSERT INTO logs(system_id, info, date, time) VALUES(%s, %s, %s, %s);'
        values = (system_id, info, date, time)
        return self._commit_sql(sql, values)

    def get_logs(self, system_id):
        """get logs from database for user/system

        args:
            system_id: str

        returns:
            [{info, date, time}]
        """
        sql = 'SELECT info, date, time FROM logs WHERE system_id = %s;'
        values = (system_id,)
        self._commit_sql(sql, values)
        data = self._fetch_all_data()
        if not data or len(data) == 0:
            return None
        return [{'info': log[0], 'date': log[1], 'time': log[2]} for log in data]

    def remove_log(self):
        pass

    def add_security_config(self, system_id):
        """add security config for system

        args:
            system_id: str

        returns:
            bool
        """
        sql = 'INSERT INTO securityconfig(system_id, system_armed, system_breached) VALUES(%s, %s, %s);'
        values = (system_id, False, False)
        return self._commit_sql(sql, values)

    def update_security_config(self, system_id, system_armed=False, system_breached=False):
        """update security config for system

        args:
            system_id: str
            system_armed: bool (Default=False)
            system_breached: bool (Default=False)

        returns:
            bool
        """
        sql = 'UPDATE securityconfig SET system_armed = %s, system_breached = %s WHERE system_id = %s'
        values = (system_armed, system_breached, system_id)
        return self._commit_sql(sql, values)

    def remove_security_config(self, system_id):
        """remove security config for system from database

        args:
            system_id: str

        returns:
            bool
        """
        sql = 'DELETE FROM securityconfig WHERE system_id = %s;'
        values = (system_id,)
        return self._commit_sql(sql, values)

    def get_security_config(self, system_id):
        """get security config from database for system

        args:
            system_id: str

        returns:
            {system_armed, system_breached}
        """
        sql = 'SELECT system_armed, system_breached FROM securityconfig WHERE system_id = %s'
        values = (system_id,)
        self._commit_sql(sql, values)
        data = self._fetch_one_data()
        if not data or len(data) == 0:
            return None
        return {'system_armed': data[0], 'system_breached': data[1]}

    def clear_all_tables(self):
        """clear all data from database"""
        for table in self.tables:
            sql = 'TRUNCATE TABLE {0};'.format(table)
            success = self._commit_sql(sql, ())
            if success:
                _logger.debug('Successfully cleared table [{0}]'.format(table))
