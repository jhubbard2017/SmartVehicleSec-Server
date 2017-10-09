# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

from securityserverpy.restAPI.restapi import RestAPI

_SUCCESS_CODE = 201
_FAILURE_CODE = 404

app = Flask(__name__)

class SecurityServer(object):
    """Centralized server to communicate both with mobile app client and raspberry pi client

    SecurityServer module uses Flask to allow the server to operate as a REST API server

    Using this approach, we don't have to manager connections to clients and we can literally "rest"
    when the client doesn't need to send a command or retrieve data. Only when the client needs it do we actually
    do the work.

    The two key components of this server are the FLASK REST API and the Postgres database.
    """

    def __init__(self, host, port, testing=False, dev=False):
        """constructor method for SecurityServer"""
        self.restapi = RestAPI(host, port, testing, dev)

    def start(self):
        """start the server"""
        self.restapi.start()

    def save_settings(self):
        """save settings"""
        self.restapi.save_settings()