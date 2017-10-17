# -*- coding: utf-8 -*-
#
# authentication module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.routes import verify_request, error_response, success_response, database, app


class Authentication(object):

    _ROOT_PATH = '/authentication'

    def __init__(self):

        # Use inner methods so self pointer can be accessed

        @app.route('{0}/login'.format(self._ROOT_PATH), methods=['POST'])
        def login():
            """log in a user

            request_data:
                email: str
                password: str
            """
            required_data_keys = ['email', 'password']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            # Check if user exists and password is correct
            user = database.verify_user(request.json['email'], request.json['password'])
            if not user: return error_response('User does not exist')

            # Check if user is already logged in
            if user['logged_in']: return error_response('User already logged in')

            # Update auth status for user
            if not database.update_user(request.json['email'], logged_in=True):
                return error_response('Failure logging in user')

            return success_response(request.path)

        @app.route('{0}/logout'.format(self._ROOT_PATH), methods=['POST'])
        def logout():
            """log out a user

            required_data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            # Check if user exists and password is correct
            user = database.verify_user(request.json['email'], request.json['password'])
            if not user: return error_response('User does not exist')

            # Check if user is already logged out
            if not user['logged_in']: return error_response('User not logged in')

            # Update auth status for user
            if not database.update_user(request.json['email'], logged_in=False):
                return error_response('Failure logging out user')

            return success_response(request.path)

        @app.route('{0}/forgot_password'.format(self._ROOT_PATH), methods=['POST'])
        def forgot_password():
            """forgot password, update user password

            required_data:
                email: str

            Todo: Implement method
            """
            pass
