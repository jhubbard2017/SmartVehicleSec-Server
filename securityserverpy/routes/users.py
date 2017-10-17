# -*- coding: utf-8 -*-
#
# users module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.routes import verify_request, error_response, success_response, database, app


class Users(object):

    _ROOT_PATH = '/users'

    def __init__(self):
        # Use inner methods so self pointer can be accessed

        @app.route('{0}/add'.format(self._ROOT_PATH), methods=['POST'])
        def add_user():
            """add a user

            required_data:
                firstname: str
                lastname: str
                email: str
                phone: str
                vehicle: str
                system_id: str
                password: str
            """
            required_data_keys = ['firstname', 'lastname', 'email', 'phone', 'vehicle', 'system_id', 'password']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            # Check if user exists and password is correct
            user = database.verify_user(request.json['email'], request.json['password'])
            if user: return error_response('User already exist')

            # Add user
            if not database.add_user(
                    request.json['email'], request.json['password'], request.json['firstname'],
                    request.json['lastname'], request.json['phone'], request.json['vehicle'], request.json['system_id']
            ):
                return error_response('Unable to add user')

            return success_response(request.path)

        @app.route('{0}/get'.format(self._ROOT_PATH), methods=['POST'])
        def get_user():
            """get a user

            required_data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            return success_response(request.json, data=user)


        @app.route('{0}/remove'.format(self._ROOT_PATH), methods=['POST'])
        def remove_user():
            """remove a user

            required_data:
                email: str
            """
            required_data_keys = ['email']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            if not database.remove_user(request.json['email']):
                return error_response('Unable to remove user')

            return success_response(request.path)

        @app.route('{0}/update'.format(self._ROOT_PATH), methods=['POST'])
        def update_user():
            """update a user

            required_data:
                firstname: str
                lastname: str
                email: str
                phone: str
                vehicle: str
                system_id: str
            """
            required_data_keys = ['firstname', 'lastname', 'email', 'phone', 'vehicle', 'system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            user = database.get_user(request.json['email'])
            if not user: return error_response('User does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            if not database.update_user(
                    request.json['email'], firstname=request.json['firstname'], lastname=request.json['lastname'],
                    phone=request.json['phone'], vehicle=request.json['vehicle'], system_id=request.json['system_id']
            ):
                return error_response('Unable to update user information')

            return success_response(request.path)

        @app.route('{0}/change_password'.format(self._ROOT_PATH), methods=['POST'])
        def change_user_password():
            """forgot password, update user password

            required_data:
                email: str
                old_password: str
                new_password: str
            """
            required_data_keys = ['email', 'old_password', 'new_password']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            # Check if user exists and password is correct
            user = database.verify_user(request.json['email'], request.json['old_password'])
            if not user: return error_response('USer does not exist')
            if not user['logged_in']: return error_response('User not authenticated')

            # Update user password
            if not database.update_user(request.json['email'], password=request.json['new_password']):
                return error_response('Unable to update password')

            return success_response(request.path)
