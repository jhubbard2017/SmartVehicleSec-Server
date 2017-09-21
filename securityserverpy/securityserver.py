# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import time
import datetime
from flask import Flask, jsonify, request
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

    def __init__(self, host, port, testing=False, dev=False):
        """constructor method for SecurityServer"""
        self.host = host
        self.port = port
        self.testing = testing
        self.dev = dev

        # Initialize the database
        self.database = Database()
        self.panic_response = PanicResponse()

        # To make the REST API (Flask) methods work, we use inner methods
        # Also, all api request from the user requires some type of data, which is shown in each method.
        # In order to recieve a successful request code and expected data, the device MAC address must exist in the database

        def abort(message):
            """error handling method for FLASK

            args:
                message: str

            returns:
                {code: int, data: bool, message: str}
            """
            return jsonify({'code': _FAILURE_CODE, 'data': False, 'message': message})

        @app.route('/system/security_config', methods=['POST'])
        def get_security_config():
            """API route to get system_armed security config value

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json and not 'rd_mac_address' in request.json:
                _logger.debug("No device found in request data")
                return abort('No device found')
            if 'rd_mac_address' in request.json:
                rd_mac_address = request.json['rd_mac_address']
            else:
                md_mac_address = request.json['md_mac_address']
                rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                return abort('Failed to get security system from server')

            security_config = self.database.get_security_config(rd_mac_address)
            if not security_config:
                _logger.debug('Failed to get security config for [{0}]'.format(rd_mac_address))
                return abort('Failed to get security system from server')

            _logger.debug("Successful! Sending security config to client [{0}]".format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': security_config})

        @app.route('/system/add_contacts', methods=['POST'])
        def add_contacts():
            """API route to add trustworthy contacts for a raspberry pi system

            required data:
                md_mac_address: str
                contacts: [{}]
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                return abort('Failed to get security system from server')

            contacts = request.json['contacts']
            for contact in contacts:
                if not self.database.add_contact(rd_mac_address, contact['name'], contact['email'], contact['phone']):
                    _logger.debug('Failed to add contact [{0}] for [{1}]'.format(contact['name'], rd_mac_address))
                    return abort('Failed to add contact recipients')

            if not self.database.add_log(rd_mac_address, 'Added security contacts.'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Added contacts for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/update_contacts', methods=['POST'])
        def update_contacts():
            """API route to update trustworthy contacts for a raspberry pi system

            required data:
                md_mac_address: str
                contacts: [{}]
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                return abort('Failed to get security system from server')

            if not self.database.remove_all_contacts(rd_mac_address):
                _logger.debug('Failed to remove contacts to prepare for update [{0}]'.format(rd_mac_address))
                return abort('Failed to update contact recipients')

            contacts = request.json['contacts']
            for contact in contacts:
                if not self.database.add_contact(rd_mac_address, contact['name'], contact['email'], contact['phone']):
                    _logger.debug('Failed to update contact [{0}] for [{1}]'.format(contact['name'], rd_mac_address))
                    return abort('Failed to update contact recipients')

            if not self.database.add_log(rd_mac_address, 'Updated security contacts.'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Updated contacts for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_contacts', methods=['POST'])
        def get_contacts():
            """API route to get contacts for a specific mobile/system device

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from Database')
                return abort('Failed to get security system from server')

            contacts = self.database.get_contacts(rd_mac_address)
            if not contacts:
                _logger.debug('Failed to get contacts from database for [{0}]'.format(rd_mac_address))
                return abort('Failed to get contact recipients')

            _logger.debug('Sending contacts to device [{0}]'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': contacts})


        @app.route('/system/add_new_device', methods=['POST'])
        def add_new_device():
            """API route to add new mobile device and associated raspberry pi device to server

            Things for this method to do:
                add mobile device to database
                add associated rpi device to database

            required data:
                md_mac_address: str
                name: str,
                email: str,
                vehicle: str,
                rd_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            # Add mobile device to database
            md_mac_address = request.json['md_mac_address']
            name = request.json['name']
            email = request.json['email']
            phone = request.json['phone']
            vehicle = request.json['vehicle']
            if not self.database.add_mobile_device(md_mac_address, name, email, phone, vehicle):
                _logger.debug('Failed to add mobile device [{0}]'.format(md_mac_address))
                return abort('Failed to add device to server')

            # Add raspberry pi for mobile device to database
            rd_mac_address = request.json['rd_mac_address']
            if not self.database.add_raspberry_pi_device(md_mac_address, rd_mac_address):
                _logger.debug('Failed to add raspberry pi device [{0}]'.format(rd_mac_address))
                return abort('Failed to add security system to server')

            if not self.database.add_log(rd_mac_address, 'Added new device: [{0}]'.format(name)):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Added new devices [{0}] [{1}]".format(md_mac_address, rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_device_info', methods=['POST'])
        def get_device_info():
            """API route to get mobile device information

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            info = self.database.get_mobile_device_information(md_mac_address)
            if not info:
                _logger.debug('Error getting information for [{0}]'.format(md_mac_address))
                return abort("Error getting device information")

            _logger.debug('Sending mobile device information for [{0}]'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': info})

        @app.route('/system/update_device_info', methods=['POST'])
        def update_device_info():
            """API route to update mobile device information

            required data:
                md_mac_address: str
                name: str
                email: str
                phone: str
                vehicle: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            name = request.json['name']
            email = request.json['email']
            phone = request.json['phone']
            vehicle = request.json['vehicle']
            if not self.database.update_mobile_device(md_mac_address, name=name, email=email, phone=phone, vehicle=vehicle):
                _logger.debug('Error updating information for [{0}]'.format(md_mac_address))
                return abort("Error updating device information")

            _logger.debug('Updated mobile device information for [{0}]'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_md_device', methods=['POST'])
        def get_device():
            """API route to check if mobile device exist

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            if not self.database.get_mobile_device(md_mac_address):
                _logger.debug('Mobile device [{0}] does not exist'.format(md_mac_address))
                return jsonify({'code': _SUCCESS_CODE, 'data': False})

            _logger.debug('Mobile device [{0}] already exist'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_rd_device', methods=['POST'])
        def get_rd_device():
            """API route to check if mobile device exist

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            if not self.database.get_raspberry_pi_device(md_mac_address):
                _logger.debug('Security device for [{0}] does not exist'.format(md_mac_address))
                return jsonify({'code': _SUCCESS_CODE, 'data': False})

            _logger.debug('Security device for [{0}] already exist'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/arm', methods=['POST'])
        def arm_system():
            """API route to arm a security system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            if not self.database.update_security_config(rd_mac_address, system_armed=True):
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                return abort('Failed to arm system.')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # send command to raspberry pi
            url = 'http://{0}:{1}/system/arm'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            if not self.database.add_log(rd_mac_address, 'System armed'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Armed system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/disarm', methods=['POST'])
        def disarm_system():
            """API route to disarm a security system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            if not self.database.update_security_config(rd_mac_address, system_armed=False):
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                return abort('Failed to disarm system')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # send command to raspberry pi
            url = 'http://{0}:{1}/system/disarm'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            if not self.database.add_log(rd_mac_address, 'System disarmed'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Disarmed system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/logs', methods=['POST'])
        def get_logs():
            """API route to get logs for a security system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            logs = self.database.get_logs(rd_mac_address)
            if not logs:
                _logger.debug('Failed to get logs for raspberry pi device [{0}]'.format(rd_mac_address))
                return abort('Failed to get logs from server')

            _logger.debug("Successful! Sending logs from [{0}] to [{1}]".format(rd_mac_address, md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': logs})

        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            """API route to set security config as false alarm

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            if not self.database.update_security_config(rd_mac_address, system_breached=False):
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                return abort('Failed to set breach as false alarm')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # send request to raspberry pi
            url = 'http://{0}:{1}/system/false_alarm'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            if not self.database.add_log(rd_mac_address, 'Security breach false alarm'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Updated security config for system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/location', methods=["POST"])
        def get_location_coordinates():
            """API route to get gps location coordinates of a raspberry pi system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # Send request to raspberry pi and get data
            url = 'http://{0}:{1}/system/location'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            _logger.debug("Successful! Send gps coordinates from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/temperature', methods=["POST"])
        def get_temperature():
            """API route to get gps location coordinates of a raspberry pi system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # Send request to raspberry pi and get data
            url = 'http://{0}:{1}/system/temperature'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            _logger.debug("Successful! Sending temperature information from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/speedometer', methods=["POST"])
        def get_speedometer_data():
            """API route to get speedometer data from a raspberry pi system

            required data:
                md_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'md_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                _logger.debug('Failed to get raspberry pi MAC address from database')
                return abort('Failed to get security system from server')

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                _logger.debug('Failed to get raspberry pi connection from database')
                return abort('Failed to get security system from server')

            # Send request to raspberry pi and get data
            url = 'http://{0}:{1}/system/speedometer'.format(connection['ip_address'], connection['port'])
            data = self.send_request(rd_mac_address, url)
            if data == None:
                _logger.debug('Failed to send request to [{0}] [{1}]'.format(rd_mac_address, url))
                return abort('Failed to connect to security system')

            _logger.debug("Successful! Sending speedometer information from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        #-------- API calls specifically from raspberry pi (security system) -----------

        @app.route('/system/create_securityconfig', methods=['POST'])
        def create_securityconfig():
            """API route to create new security config for raspberry pi device

            required data:
                rd_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            if not self.database.add_security_config(rd_mac_address):
                _logger.debug('Failed to add security config for raspberry pi device [{0}]'.format(rd_mac_address))
                return abort('Failed to add security config')

            _logger.debug("Successful! Create security config for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/add_connection', methods=['POST'])
        def add_connection():
            """API route to add connection parameters for a raspberry pi device

            required data:
                rd_mac_address: str
                ip_address: str
                port: int
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            if not self.database.add_raspberry_pi_connection(rd_mac_address, ip_address, port):
                _logger.debug('Failed to add raspberry pi connection [{0}]'.format(rd_mac_address))
                return abort('Failed to add connection')

            _logger.debug("Successful! Added raspberry pi connection [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/update_connection', methods=['POST'])
        def update_connection():
            """API route to update connection parameters for a raspberry pi device

            required data:
                rd_mac_address: str
                ip_address: str
                port: int
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            if not self.database.update_raspberry_pi_connection(rd_mac_address, ip_address=ip_address, port=port):
                _logger.debug('Failed to update raspberry pi connection [{0}]'.format(rd_mac_address))
                return abort('Failed to update connection')

            _logger.debug("Successful! Updated raspberry pi connection [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_connection', methods=['POST'])
        def get_connection():
            """API route to check if connection exists in database

            required data:
                rd_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            connection = self.database.get_raspberry_pi_connection(rd_mac_address)

            if not connection:
                _logger.debug('Failed to get raspberry pi connection [{0}]'.format(rd_mac_address))
                return jsonify({'code': _SUCCESS_CODE, 'data': False})
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/set_breached', methods=['POST'])
        def set_system_breached():
            """API route to set system breached for particular system (SHOULD ONLY BE CALLED BY RPI)

            required data:
                rd_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            success = self.database.update_security_config(rd_mac_address, system_breached=True)
            if not success:
                _logger.debug('Failed to update security config for [{0}]'.format(rd_mac_address))
                return abort('Failed to update security config')

            # Todo: figure out way of notifying associated mobile app client

            if not self.database.add_log(rd_mac_address, 'System breached'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Updated security config for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

        @app.route('/system/panic', methods=['POST'])
        def panic_reponse():
            """API route to send panic response emails and text messages to contacts of specific system

            required data:
                rd_mac_address: str
            """
            if not request.json:
                _logger.debug("Error! JSON does not exist")
                return abort('No data found')
            if not 'rd_mac_address' in request.json:
                _logger.debug("Error! Device not found in request data.")
                return abort('No device found')

            rd_mac_address = request.json['rd_mac_address']
            contacts = self.database.get_contacts(rd_mac_address)
            if not contacts:
                _logger.debug("Failed to get contacts for [{0}]".format(rd_mac_address))
                return abort('Failed to get contacts')

            for contact in contacts:
                if not self.panic_response.send_message(contacts['email']):
                    _logger.debug("Failed to send email to[{0}]".format(contacts['email']))
                    abort('Failed to send panic response email')

            # Todo: figure out way of notifying associated mobile app client

            if not self.database.add_log(rd_mac_address, 'Panic response initiated'):
                _logger.debug('Failed to add log for [{1}]'.format(rd_mac_address))

            _logger.debug("Successful! Sent panic email to contacts from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

    def save_settings(self):
        """method is fired when the server is shut down"""
        _logger.debug('Saving security session.')
        if self.dev:
            self.database.clear_all_tables()

    def start(self):
        """starts the flask app"""
        app.run(host=self.host, port=self.port)

    def server_app(self):
        return app

    def send_request(self, rd_mac_address, url):
        """Sends http request to ip address and port connection

        args:
            rd_mac_address: str
            url: str

        returns:
            json {}
        """
        data = {'rd_mac_address': rd_mac_address}
        response = requests.post(url, json=data)
        json = response.json()
        if json['code'] != _SUCCESS_CODE:
            return None
        return json['data']
