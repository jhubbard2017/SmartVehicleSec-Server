# -*- coding: utf-8 -*-
#
# emergency contacts module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.routes import verify_request, error_response, success_response, database, app


class EmergencyContacts(object):

    _ROOT_PATH = '/emergency_contacts'

    @app.route('{0}/add'.format(_ROOT_PATH), methods=['POST'])
    def add_contacts(self):
        """adds contacts for user

        required_data:
            email: str
            contacts: [name, email, phone]
        """
        required_data_keys = ['email', 'contacts']
        status, error = verify(request.json, keys=required_data_keys, all_should_exist=True)
        if not status: return error_response(error)

        # Check if user exists and authenticated
        user = database.get_user(request.json['email'])
        if not user: return error_response('User does not exist')
        if not user['logged_in']: return error_response('User not authenticated')

        for contact in request.json['contacts']:
            if not 'name' in contact and not 'email' in contact and not 'phone' in contact:
                return error_response('Required data missing in contacts list')
            if not database.add_contact(user['system_id'], contact['name'], contact['email'], contact['phone']):
                return error_response('Unable to add contacts')

        return success_response(request.path)

    @app.route('{0}/get'.format(_ROOT_PATH), methods=['POST'])
    def get_contacts(self):
        """get contacts list for user

        required_data:
            email: str
        """
        required_data_keys = ['email']
        status, error = verify(request.json, keys=required_data_keys, all_should_exist=True)
        if not status: return error_response(error)

        # Check if user exists and authenticated
        user = database.get_user(request.json['email'])
        if not user: return error_response('User does not exist')
        if not user['logged_in']: return error_response('User not authenticated')

        contacts = database.get_contacts(user['system_id'])
        if not contacts: return error_response('Unable to get contacts for user')

        return success_response(request.path, data=contacts)

    @app.route('{0}/update'.format(_ROOT_PATH), methods=['POST'])
    def update_contacts(self):
        """update contacts list for user

        required_data:
            email: str
            contacts: [name, email, phone]
        """
        required_data_keys = ['email', 'contacts']
        status, error = verify(request.json, keys=required_data_keys, all_should_exist=True)
        if not status: return error_response(error)

        # Check if user exists and authenticated
        user = database.get_user(request.json['email'])
        if not user: return error_response('User does not exist')
        if not user['logged_in']: return error_response('User not authenticated')

        if not database.remove_all_contacts(user['system_id']):
            return error_response('Failure while updating contacts')

        for contact in request.json['contacts']:
            if not 'name' in contact and not 'email' in contact and not 'phone' in contact:
                return error_response('Required data missing in contacts list')
            if not database.add_contact(user['system_id'], contact['name'], contact['email'], contact['phone']):
                return error_response('Unable to update contacts')

        return success_response(request.path)
