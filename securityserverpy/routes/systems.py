# -*- coding: utf-8 -*-
#
# systems module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.client_requests import ClientRequests
from securityserverpy.routes import verify_request, error_response, success_response, database, app


class Systems(object):

    _ROOT_PATH = '/systems'

    def __init__(self):
        self.client_requests = ClientRequests()

        # Use inner methods so self pointer can be accessed

        @app.route('{0}/temperature'.format(self._ROOT_PATH), methods=['POST'])
        def temperature():
            """get temperature data for system

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

            data = self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='temperature')
            if not data: return error_response('Unable to complete system request')

            return success_response(request.path, data=data)

        @app.route('{0}/speedometer'.format(self._ROOT_PATH), methods=['POST'])
        def speedometer():
            """get speedometer data for system

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

            data = self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='speedometer')
            if not data: return error_response('Unable to complete system request')

            return success_response(request.path, data=data)

        @app.route('{0}/location'.format(self._ROOT_PATH), methods=['POST'])
        def location():
            """get location data for system

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

            data = self.client_requests.make_request(connection['host'], connection['port'], user['system_id'], path='location')
            if not data: return error_response('Unable to complete system request')

            return success_response(request.path, data=data)