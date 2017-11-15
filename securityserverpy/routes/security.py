# -*- coding: utf-8 -*-
#
# security module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.routes import verify_request, error_response, success_response, database, app
from securityserverpy.client_requests import ClientRequests
from securityserverpy.panic_response import PanicResponse


class Security(object):

    _ROOT_PATH = '/security'

    def __init__(self):
        self.client_requests = ClientRequests()
        self.panic_response = PanicResponse()

        # Use inner methods so self pointer can be accessed

        @app.route('{0}/get_config'.format(self._ROOT_PATH), methods=['POST'])
        def get_config():
            """get security config

            required data:
                email: str
                system_id: str
                (Only one is required)
            """
            required_data_keys = ['email', 'system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=False)
            if not status: return error_response(error)

            if not 'system_id' in request.json:
                user = database.get_user(request.json['email'])
                if not user: return error_response('User does not exist')
                if not user['logged_in']: return error_response('User not authenticated')
                system_id = user['system_id']
            else:
                system_id = request.json['system_id']

            config = database.get_security_config(system_id)
            if not config: return error_response('Unable to get security config')

            return success_response(request.path, data=config)

        @app.route('{0}/add_config'.format(self._ROOT_PATH), methods=['POST'])
        def add_config():
            """add security config

            required data:
                system_id: str
            """
            required_data_keys = ['system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            if database.get_security_config(request.json['system_id']):
                return error_response('Security config already exist')

            if not database.add_security_config(request.json['system_id']):
                return error_response('Unable to add security config')

            return success_response(request.path)

        @app.route('{0}/arm'.format(self._ROOT_PATH), methods=['POST'])
        def arm():
            """arm system

            required data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            connection = database.get_connection(user['system_id'])
            if not connection: return error_response('Unable to get connection for system', user_system=user['email'])

            if not self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='security/arm'):
                return error_response('Unable to complete system request')

            if not database.update_security_config(user['system_id'], system_armed=True):
                return error_response('Failed to update security config')

            if not database.add_log(user['system_id'], 'System armed'):
                _logger.debug('Failed to add log for [{0}]'.format(user['system_id']))

            return success_response(request.path)


        @app.route('{0}/disarm'.format(self._ROOT_PATH), methods=['POST'])
        def disarm():
            """disarm system

            required data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            connection = database.get_connection(user['system_id'])
            if not connection: return error_response('Unable to get connection for system', user_system=user['email'])

            if not self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='security/disarm'):
                return error_response('Unable to complete system request')

            if not database.update_security_config(user['system_id'], system_armed=False):
                return error_response('Failed to update security config')

            if not database.add_log(user['system_id'], 'System armed'):
                _logger.debug('Failed to add log for [{0}]'.format(user['system_id']))

            return success_response(request.path)

        @app.route('{0}/false_alarm'.format(self._ROOT_PATH), methods=['POST'])
        def false_alarm():
            """set breach as false alarm

            required data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            connection = database.get_connection(user['system_id'])
            if not connection: return error_response('Unable to get connection for system', user_system=user['email'])

            if not self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='security/false_alarm'):
                return error_response('Unable to complete system request')

            if not database.update_security_config(user['system_id'], system_breached=False):
                return error_response('Failed to update security config')

            if not database.add_log(user['system_id'], 'System breach false alarm'):
                _logger.debug('Failed to add log for [{0}]'.format(user['system_id']))

            return success_response(request.path)

        @app.route('{0}/panic'.format(self._ROOT_PATH), methods=['POST'])
        def panic():
            """panic, and send out emails to emergency contacts

            required data:
                system_id: str
            """
            required_data_keys = ['system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user_with_system_id(request.json['system_id'])
            if not user: return error_response('Unable to get associated user for system')

            contacts = database.get_contacts(request.json['system_id'])
            if not contacts: return error_response('Unable to get contacts for system')

            for contact in contacts:
                if not self.panic_response.send_message(contact['email'], user):
                    return error_response('Unable to send email to contacts for system')

            # Todo: send push notification to user

            if not database.add_log(user['system_id'], 'Panic initiated'):
                _logger.debug('Failed to add log for [{0}]'.format(user['system_id']))

            return success_response(request.path)

        @app.route('{0}/set_breach'.format(self._ROOT_PATH), methods=['POST'])
        def set_breach():
            """set system as breached

            required data:
                system_id: str
            """
            required_data_keys = ['system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            config = database.get_security_config(request.json['system_id'])
            if not config: return error_response('System does not exist')
            if config['system_breached']: return error_response('System already breached')

            if not database.update_security_config(request.json['system_id'], system_breached=True):
                return error_response('Unable to update security config')

            if not database.add_log(user['system_id'], 'System breached'):
                _logger.debug('Failed to add log for [{0}]'.format(user['system_id']))

            return success_response(request.path)

        @app.route('{0}/get_logs'.format(self._ROOT_PATH), methods=['POST'])
        def get_logs():
            """get logs for user

            required data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            logs = database.get_logs(user['system_id'])
            if not logs: return success_response(request.path, data=[])

            return success_response(request.path, data=logs)
