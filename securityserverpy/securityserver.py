# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import time
import datetime
from flask import Flask, jsonify, request, abort
import requests

from securityserverpy import _logger
from securityserverpy.database import Database
from securityserverpy.panic_response import PanicResponse

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

    # Log constants
    _USER_CONTROLLED_LOG_TYPE = 'user_controlled_type'
    _SECURITY_CONTROLLED_LOG_TYPE = 'security_controlled_type'

    def __init__(self, host, port, testing=False):
        """constructor method for SecurityServer"""
        self.host = host
        self.port = port
        self.testing = testing

        # Initialize the database
        self.database = Database()
        self.panic_response = PanicResponse()

        # To make the REST API (Flask) methods work, we use inner methods
        # Also, all api request from the user requires some type of data, which is shown in each method.
        # In order to recieve a successful request code and expected data, the device MAC address must exist in the database

        # Error handling
        @app.errorhandler(_FAILURE_CODE)
        def not_found(error):
            return jsonify({'code': _FAILURE_CODE,'data': 0})

        @app.route('/system/security_config', methods=['POST'])
        def get_security_config():
            """API route to get system_armed security config value

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                abort(_FAILURE_CODE)

            security_config = self.database.get_security_config(rd_mac_address)
            if not security_config:
                _logger.debug('Failed to get security config for [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            _logger.debug("Successful! Sending security config to client [{0}]".format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': security_config})

        @app.route('/system/add_contacts', methods=['POST'])
        def add_contacts():
            """API route to add trustworthy contacts for a raspberry pi system

            required data:
                md_mac_address: str
                contacts: [{}]
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                abort(_FAILURE_CODE)

            contacts = request.json['contacts']
            for contact in contacts:
                success = self.database.add_contact(rd_mac_address, contact['name'], contact['email'], contact['phone'])
                if not success:
                    _logger.debug('Failed to add contact [{0}] for [{1}]'.format(contact['name'], rd_mac_address))
                    abort(_FAILURE_CODE)

            _logger.debug("Successful! Added contacts for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/update_contacts', methods=['POST'])
        def update_contacts():
            """API route to update trustworthy contacts for a raspberry pi system

            required data:
                md_mac_address: str
                contacts: [{}]
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                abort(_FAILURE_CODE)

            contacts = request.json['contacts']
            for contact in contacts:
                success = self.database.update_contact(rd_mac_address, contact['name'],
                                                       email=contact['email'], phone=contact['phone'])
                if not success:
                    _logger.debug('Failed to update contact [{0}] for [{1}]'.format(contact['name'], rd_mac_address))
                    abort(_FAILURE_CODE)

            _logger.debug("Successful! Updated contacts for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/add_new_device', methods=['POST'])
        def add_new_device():
            """API route to add new mobile device and associated raspberry pi device to server

            required data:
                md_mac_address: str
                name: str
                rd_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            name = request.json['name']
            success = self.database.add_mobile_device(md_mac_address, name)
            if not success:
                _logger.debug('Failed to add mobile device [{0}]'.format(md_mac_address))
                abort(_FAILURE_CODE)

            rd_mac_address = request.json['rd_mac_address']
            success = self.database.add_raspberry_pi_device(md_mac_address, rd_mac_address)
            if not success:
                _logger.debug('Failed to add raspberry pi device [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            _logger.debug("Successful! Added new devices [{0}] [{1}]".format(md_mac_address, rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/add_connection', methods=['POST'])
        def add_connection():
            """API route to add connection parameters for a raspberry pi device

            required data:
                rd_mac_address: str
                ip_address: str
                port: int
            """
            if not request.json or not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            success = self.database.add_raspberry_pi_connection(rd_mac_address, ip_address, port)
            if not success:
                _logger.debug('Failed to add raspberry pi connection [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            _logger.debug("Successful! Added raspberry pi connection [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/update_connection', methods=['POST'])
        def update_connection():
            """API route to update connection parameters for a raspberry pi device

            required data:
                rd_mac_address: str
                ip_address: str
                port: int
            """
            if not request.json or not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            success = self.database.update_raspberry_pi_connection(rd_mac_address, ip_address=ip_address, port=port)
            if not success:
                _logger.debug('Failed to update raspberry pi connection [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            _logger.debug("Successful! Updated raspberry pi connection [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/arm', methods=['POST'])
        def arm_system():
            """API route to arm a security system

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            success = self.database.update_security_config(rd_mac_address, system_armed=True)
            if not success:
                _logger.debug('Failed to set update security config for [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            ip_address, port = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not ip_address and not port:
                _logger.debug('Failed to get raspberry pi connection from database')
                abort(_FAILURE_CODE)

            # send command to raspberry pi
            success = self._disarm_system(ip_address, port)

            _logger.debug("Successful! Armed system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/disarm', methods=['POST'])
        def disarm_system():
            """API route to disarm a security system

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            success = self.database.update_security_config(rd_mac_address, system_armed=False)
            if not success:
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)
            ip_address, port = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not ip_address and not port:
                _logger.debug('Failed to get raspberry pi connection from database')
                abort(_FAILURE_CODE)

            # send command to raspberry pi
            success = self._disarm_system(ip_address, port)

            _logger.debug("Successful! Disarmed system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/logs', methods=['GET'])
        def get_logs():
            """API route to get logs for a security system

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            user_logs = self.database.get_logs(rd_mac_address, SecurityServer._USER_CONTROLLED_LOG_TYPE)
            system_logs = self.database.get_logs(rd_mac_address, SecurityServer._SECURITY_CONTROLLED_LOG_TYPE)
            if not user_logs and not system_logs:
                _logger.debug('Failed to get logs for raspberry pi device [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            all_logs = {
                'user_logs': user_logs,
                'system_logs': system_logs
            }

            _logger.debug("Successful! Sending logs from [{0}] to [{1}]".format(rd_mac_address, md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': all_logs})

        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            """API route to set security config as false alarm

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            success = self.database.update_security_config(rd_mac_address, system_breached=False)
            if not success:
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            ip_address, port = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not ip_address and not port:
                _logger.debug('Failed to get raspberry pi connection from database')
                abort(_FAILURE_CODE)

            # send request to raspberry pi
            success = self._set_false_alarm_for_system(ip_address, port)

            _logger.debug("Successful! Updated security config for system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/location', methods=["POST"])
        def get_location_coordinates():
            """API route to get gps location coordinates of a raspberry pi system

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            ip_address, port = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not ip_address and not port:
                _logger.debug('Failed to get raspberry pi connection from database')
                abort(_FAILURE_CODE)

            # Send request to raspberry pi and get data
            data = self._get_gps_location_from_system(ip_address, port)

            _logger.debug("Successful! Send gps coordinates from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/temperature', methods=["POST"])
        def get_temperature():
            """API route to get gps location coordinates of a raspberry pi system

            required data:
                md_mac_address: str
            """
            if not request.json or not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                abort(_FAILURE_CODE)

            ip_address, port = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not ip_address and not port:
                _logger.debug('Failed to get raspberry pi connection from database')
                abort(_FAILURE_CODE)

            # Send request to raspberry pi and get data
            data = self._get_temperature_data_from_system(ip_address, port)

            _logger.debug("Successful! Sending temperature information from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        #-------- API calls specifically from raspberry pi (security system) -----------

        @app.route('system/set_breached', method=['POST'])
        def set_system_breached():
            """API route to set system breached for particular system (SHOULD ONLY BE CALLED BY RPI)

            required data:
                rd_mac_address: str
            """
            if not request.json or not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            rd_mac_address = request.json['rd_mac_address']
            success = self.database.update_security_config(rd_mac_address, system_breached=True)
            if not success:
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                abort(_FAILURE_CODE)

            # Todo: figure out way of notifying associated mobile app client

            _logger.debug("Successful! Updated security config for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('system/panic', method=['POST'])
        def panic_reponse():
            """API route to send panic response emails and text messages to contacts of specific system

            required data:
                rd_mac_address: str
            """
            if not request.json or not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                abort(_FAILURE_CODE)

            rd_mac_address = request.json['rd_mac_address']
            contacts = self.database.get_contacts(rd_mac_address)
            if not contacts:
                _logger.debug("Failed to get contacts for [{0}]".format(rd_mac_address))
                abort(_FAILURE_CODE)

            for contact in contacts:
                if not self.panic_response.send_message(contacts['email']):
                    _logger.debug("Failed to send email to[{0}]".format(contacts['email']))
                    abort(_FAILURE_CODE)

            # Todo: figure out way of notifying associated mobile app client

            _logger.debug("Successful! Sent panic email to contacts from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

    def save_settings(self):
        """method is fired when the server is shut down"""
        _logger.debug('Saving security session.')
        if self.testing:
            self.database.clear_all_tables()

    def start(self):
        """starts the flask app"""
        app.run(host=self.host, port=self.http_port)

    def server_app(self):
        return app

    def _get_temperature_data_from_system(self, ip_address, port):
        """Sends http request to ip address and port to get current temperature data

        args:
            ip_address: str
            port: int

        returns:
            dict
        """
        url = 'http://{0}:{1}/system/temperature'.format(ip_address, port)
        temp = requests.get(url)
        temp = temp.json()
        data = {
            "celsius": temp['celsius'],
            "fahrenheit": float(location["fahrenheit"])
        }
        return data

    def _get_gps_location_from_system(self, ip_address, port):
        """Sends http request to ip address and port to get current gps data

        args:
            ip_address: str
            port: int

        returns:
            dict
        """
        url = 'http://{0}:{1}/system/location'.format(ip_address, port)
        location = requests.get(url)
        location = location.json()
        position = {
            "latitude": float(location["latitude"]),
            "longitude": float(location["longitude"])
        }
        return position

    def _set_false_alarm_for_system(self, ip_address, port):
        """Sends http request to ip address and port for false alarm

        args:
            ip_address: str
            port: int

        returns:
            dict
        """
        url = 'http://{0}:{1}/system/false_alarm'.format(ip_address, port)
        response = requests.get(url)
        response = success.json()
        return response['success']

    def _arm_system(self, ip_address, port):
        """Sends http request to ip address and port to arm system

        args:
            ip_address: str
            port: int

        returns:
            dict
        """
        url = 'http://{0}:{1}/system/arm'.format(ip_address, port)
        response = requests.get(url)
        response = success.json()
        return response['success']

    def _disarm_system(self, ip_address, port):
        """Sends http request to ip address and port to disarm system

        args:
            ip_address: str
            port: int

        returns:
            dict
        """
        url = 'http://{0}:{1}/system/disarm'.format(ip_address, port)
        response = requests.get(url)
        response = success.json()
        return response['success']
