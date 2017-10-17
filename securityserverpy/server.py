# -*- coding: utf-8 -*-
#
# server module
#

from securityserverpy import _logger
from securityserverpy.routes import database, app
from securityserverpy.routes.authentication import Authentication
from securityserverpy.routes.users import Users
from securityserverpy.routes.emergency_contacts import EmergencyContacts
from securityserverpy.routes.connections import Connections
from securityserverpy.routes.security import Security
from securityserverpy.routes.systems import Systems


class Server(object):

    def __init__(self, host, port, dev=False):
        """constructor method"""
        self.host = host
        self.port = port

        # Development mode
        self.dev = dev

        # API Routes
        authentication = Authentication()
        users = Users()
        emergency_contacts = EmergencyContacts()
        connections = Connections()
        security = Security()
        systems = Systems()

    def start(self):
        """start the server"""
        app.run(host=self.host, port=self.port)

    def save_settings(self):
        """save settings"""
        _logger.debug('Saving security session.')
        if self.dev:
            database.clear_all_tables()