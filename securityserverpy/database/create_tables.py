# -*- coding: utf-8 -*-
#
# utility class connecting and controlling postgres database
#

import psycopg2
from configparser import ConfigParser

_CONFIG_PATH = 'securityserverpy/Database/database.ini'

def _get_database_info(filename, section='postgresql'):
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

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE users (
            email VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            firstname VARCHAR(255) NOT NULL,
            lastname VARCHAR(255) NOT NULL,
            phone VARCHAR(255) NOT NULL,
            vehicle VARCHAR(255) NOT NULL,
            system_id VARCHAR(255) NOT NULL,
            logged_in BOOLEAN NOT NULL
        )
        """,
        """
        CREATE TABLE connections (
                system_id VARCHAR(255) PRIMARY KEY,
                host VARCHAR(255) NOT NULL,
                port INT NOT NULL
        )
        """,
        """
        CREATE TABLE securityconfig (
                system_id VARCHAR(255) PRIMARY KEY,
                system_armed BOOLEAN NOT NULL,
                system_breached BOOLEAN NOT NULL
        )
        """,
        """
        CREATE TABLE logs (
                system_id VARCHAR(255) NOT NULL,
                info VARCHAR(255) NOT NULL,
                date VARCHAR(255) NOT NULL,
                time VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE contacts (
                system_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(255) NOT NULL
        )
        """
    )
    conn = None
    try:
        # read the connection parameters
        params = _get_database_info(_CONFIG_PATH)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()