# -*- coding: utf-8 -*-
#
# module for handling rest api calls from clients
#

from flask import Flask
from flask import jsonify
from flask import request

from securityserverpy import _logger
from securityserverpy.Flask.error_handling import APIErrorHandling
from securityserverpy.client_requests import ClientRequests
from securityserverpy.Database.database import Database
from securityserverpy.panic_response import PanicResponse

app = Flask(__name__)

class RestAPI(object):
    """Module for controlling rest api calls and methods"""

    # Constants
    _SUCCESS_CODE = 201
    _FAILURE_CODE = 404

    def __init__(self, host, port, testing=False, dev=False):
        """constructor method"""

        self.host = host
        self.port = port

        # Development mode variables
        self.testing = testing
        self.dev = dev

        self.database = Database()
        self.panic_response = PanicResponse()
        self.error_handling = FlaskErrorHandling()
        self.client_requests = ClientRequests()

        # We use inner methods for the flask api route methods so that they can access the self pointer
        # of this class.

        @app.route('/system/security_config', methods=['POST'])
        def get_security_config():
            """API route to get system_armed security config value

            required data:
                md_mac_address: str || rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address', 'rd_mac_address'])
            if not status:
                return self.abort_with_message(error)

            if 'rd_mac_address' in request.json:
                rd_mac_address = request.json['rd_mac_address']
            else:
                md_mac_address = request.json['md_mac_address']
                rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)

            if not rd_mac_address:
                error = 'Failed to get client id'
                return self.abort_with_message(error, device=md_mac_address)

            security_config = self.database.get_security_config(rd_mac_address)
            if not security_config:
                error = 'Failed to get security config from server'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Sending security config for [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': security_config})

        @app.route('/system/add_contacts', methods=['POST'])
        def add_contacts():
            """API route to add trustworthy contacts for a raspberry pi system

            required data:
                md_mac_address: str
                contacts: [{}]
            """
            status, error = self.error_handling.check_system_request(
                request.json, keys=['md_mac_address', 'contacts'], all_should_exists=True
            )
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get client from server'
                return self.abort_with_message(error, device=md_mac_address)

            contacts = request.json['contacts']
            for contact in contacts:
                if not self.database.add_contact(rd_mac_address, contact['name'], contact['email'], contact['phone']):
                    error = 'Failed to add contact recipients'
                    return self.abort_with_message(error, device=rd_mac_address)

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
            status, error = self.error_handling.check_system_request(
                request.json, keys=['md_mac_address', 'contacts'], all_should_exists=True
            )
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get client from server'
                return self.abort_with_message(error, device=md_mac_address)

            if not self.database.remove_all_contacts(rd_mac_address):
                error = 'Failed to remove current contact recipients'
                return self.abort_with_message(error, device=rd_mac_address)

            contacts = request.json['contacts']
            for contact in contacts:
                if not self.database.add_contact(rd_mac_address, contact['name'], contact['email'], contact['phone']):
                    error = 'Failed to update contact recipients'
                    return self.abort_with_message(error, device=rd_mac_address)

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
            status, error = self.error_handling.check_system_request(
                request.json, keys=['md_mac_address'], all_should_exists=True
            )
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            contacts = self.database.get_contacts(rd_mac_address)
            if not contacts:
                error = 'Failed to get contact recipients'
                return self.abort_with_message(error, device=rd_mac_address)

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
            keys = ['md_mac_address', 'name', 'email', 'vehicle', 'rd_mac_address']
            status, error = self.error_handling.check_system_request(request.json, keys, all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

            # Add mobile device to database
            md_mac_address = request.json['md_mac_address']
            name = request.json['name']
            email = request.json['email']
            phone = request.json['phone']
            vehicle = request.json['vehicle']
            if not self.database.add_mobile_device(md_mac_address, name, email, phone, vehicle):
                error = 'Failed to add device to server'
                return self.abort_with_message(error, device=md_mac_address)

            # Add raspberry pi for mobile device to database
            rd_mac_address = request.json['rd_mac_address']
            if not self.database.add_raspberry_pi_device(md_mac_address, rd_mac_address):
                error = 'Failed to add security system to server'
                return self.abort_with_message(error, device=rd_mac_address)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            info = self.database.get_mobile_device_information(md_mac_address)
            if not info:
                error = 'Error getting device information'
                return self.abort_with_message(error, device=md_mac_address)

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
            keys = ['md_mac_address', 'name', 'email', 'phone', 'vehicle']
            status, error = self.error_handling.check_system_request(request.json, keys=keys, all_should_exists=True)
            if not status:
                self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            name = request.json['name']
            email = request.json['email']
            phone = request.json['phone']
            vehicle = request.json['vehicle']
            if not self.database.update_mobile_device(md_mac_address, name=name, email=email, phone=phone, vehicle=vehicle):
                error = 'Failed to update device information'
                return self.abort_with_message(error, device=md_mac_address)

            _logger.debug('Updated mobile device information for [{0}]'.format(md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_md_device', methods=['POST'])
        def get_device():
            """API route to check if mobile device exist

            required data:
                md_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            if not self.database.update_security_config(rd_mac_address, system_armed=True):
                error = 'Failed to update security config'
                return self.abort_with_message(error, device=rd_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get connection from server'
                return self.abort_with_message(error, device=rd_mac_address)

            # send command to raspberry pi
            if not self.client_requests.arm_system(connection['ip_address'], connection['port'], rd_mac_address):
                error = 'Failed to send request to client'
                return self.abort_with_message(error, device=rd_mac_address)

            if not self.database.add_log(rd_mac_address, 'System armed'):
                _logger.debug('Failed to add log for [{0}]'.format(rd_mac_address))

            _logger.debug("Successful! Armed system [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/disarm', methods=['POST'])
        def disarm_system():
            """API route to disarm a security system

            required data:
                md_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error)

            if not self.database.update_security_config(rd_mac_address, system_armed=False):
                error = 'Failed to update security config'
                return self.abort_with_message(error, device=rd_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=rd_mac_address)

            # send command to raspberry pi
            if not self.client_requests.disarm(connection['ip_address'], connection['port'], rd_mac_address):
                error = 'Failed to send request to client'
                return self.abort_with_message(error, rd_mac_address)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            logs = self.database.get_logs(rd_mac_address)
            if not logs:
                error = 'Failed to get logs from server'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Sending logs from [{0}] to [{1}]".format(rd_mac_address, md_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': logs})

        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            """API route to set security config as false alarm

            required data:
                md_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            if not self.database.update_security_config(rd_mac_address, system_breached=False):
                error = 'Failed to update security config'
                return self.abort_with_message(error, device=rd_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=rd_mac_address)

            if not self.client_requests.false_alarm(connection['ip_address'], connection['port'], rd_mac_address):
                error = 'Failed to send request to client'
                return self.abort_with_message(error, device=rd_mac_address)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=rd_mac_address)

            data = self.client_requests.get_data(connection['ip_address'], connection['port'], rd_mac_address, path='location')
            if not data:
                error = 'Failed to send request to client'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Send gps coordinates from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/temperature', methods=["POST"])
        def get_temperature():
            """API route to get gps location coordinates of a raspberry pi system

            required data:
                md_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=rd_mac_address)

            # Send request to raspberry pi and get data
            data = self.client_requests.get_data(connection['ip_address'], connection['port'], rd_mac_address, path='temperature')
            if not data:
                error = 'Failed to send request to client'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Sending temperature information from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/speedometer', methods=["POST"])
        def get_speedometer_data():
            """API route to get speedometer data from a raspberry pi system

            required data:
                md_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['md_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            md_mac_address = request.json['md_mac_address']
            rd_mac_address = self.database.get_raspberry_pi_device(md_mac_address)
            if not rd_mac_address:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=md_mac_address)

            connection = self.database.get_raspberry_pi_connection(rd_mac_address)
            if not connection:
                error = 'Failed to get security system from server'
                return self.abort_with_message(error, device=rd_mac_address)

            # Send request to raspberry pi and get data
            data = self.client_requests.get_data(connection['ip_address'], connection['port'], rd_mac_address, path='speedometer')
            if not data:
                error = 'Failed to send request to client'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Sending speedometer information from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': data})


        #-------- API calls specifically from raspberry pi (security system) -----------

        @app.route('/system/create_securityconfig', methods=['POST'])
        def create_securityconfig():
            """API route to create new security config for raspberry pi device

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['rd_mac_address'], all_should_exist=True)
            if not status:
                return self.abort_with_message(error)

            rd_mac_address = request.json['rd_mac_address']
            if not self.database.add_security_config(rd_mac_address):
                error = 'Failed to add security config'
                return self.abort_with_message(error, device=rd_mac_address)

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
            keys = ['rd_mac_address', 'ip_address', 'port']
            status, error = self.error_handling.check_system_request(request.json, keys=keys, all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            if not self.database.add_raspberry_pi_connection(rd_mac_address, ip_address, port):
                error = 'Failed to add connection'
                return self.abort_with_message(error, device=rd_mac_address)

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
            keys = ['rd_mac_address', 'ip_address', 'port']
            status, error = self.error_handling.check_system_request(request.json, keys=keys, all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

            rd_mac_address = request.json['rd_mac_address']
            ip_address = request.json['ip_address']
            port = request.json['port']
            if not self.database.update_raspberry_pi_connection(rd_mac_address, ip_address=ip_address, port=port):
                error = 'Failed to updated connection'
                return self.abort_with_message(error, device=rd_mac_address)

            _logger.debug("Successful! Updated raspberry pi connection [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/get_connection', methods=['POST'])
        def get_connection():
            """API route to check if connection exists in database

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json, keys=['rd_mac_address'], all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['rd_mac_address'], all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

            rd_mac_address = request.json['rd_mac_address']
            success = self.database.update_security_config(rd_mac_address, system_breached=True)
            if not success:
                error = 'Failed to update security config'
                return self.abort_with_message(error, device=rd_mac_address)

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
            status, error = self.error_handling.check_system_request(request.json, keys=['rd_mac_address'], all_should_exists=True)
            if not status:
                return self.abort_with_message(error)

            rd_mac_address = request.json['rd_mac_address']
            contacts = self.database.get_contacts(rd_mac_address)
            if not contacts:
                error = 'Failed to get contacts'
                self.abort_with_message(error, device=rd_mac_address)

            md_mac_address = self.database.get_mobile_device_with_rd(rd_mac_address)
            if not md_mac_address:
                error = 'Failed to get associated device'
                self.abort_with_message(error, device=rd_mac_address)

            device_info = self.database.get_mobile_device_information(md_mac_address)
            if not device_info:
                error = 'Failed to get device information'
                self.abort_with_message(error, device=md_mac_address)

            for contact in contacts:
                if not self.panic_response.send_message(contact['email'], device_info):
                    error = 'Failed to send email to panic recipient'
                    return self.abort_with_message(error, device=contact['email'])

            # Todo: figure out way of notifying associated mobile app client

            if not self.database.add_log(rd_mac_address, 'Panic response initiated'):
                _logger.debug('Failed to add log for [{1}]'.format(rd_mac_address))

            _logger.debug("Successful! Sent panic email to contacts from [{0}]".format(rd_mac_address))
            return jsonify({'code': _SUCCESS_CODE, 'data': success})

    def abort_with_message(self, error, device='Unknown'):
        """error handling method for FLASK API calls

        args:
            message: str

        returns:
            jsonify({code, data, message})
        """
        _logger.info('Aborting with error: [{0}] for device [{1}]'.format(message, device))
        return jsonify({'code': _FAILURE_CODE, 'message': error})

    def start(self):
        """method to start the flask server"""
        app.run(host=self.host, port=self.port)

    def save_settings(self):
        """saves settings before quiting program"""
        _logger.debug('Saving security session.')
        if self.dev:
            self.database.clear_all_tables()
