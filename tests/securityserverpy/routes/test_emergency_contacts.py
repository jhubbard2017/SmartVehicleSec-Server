# -*- coding: utf-8 -*-
#
# module for testing emergency contacts
#

import unittest
import json

from securityserverpy.routes.emergency_contacts import EmergencyContacts
from tests.mocks.database_mock import DatabaseMock
from securityserverpy.routes import app, _FAILURE_CODE, _SUCCESS_CODE
from securityserverpy.routes import _NO_DATA_MESSAGE, _EXPECTED_DATA_MISSING_MESSAGE
from tests.securityserverpy.routes import RestAPITestHelper

contacts = EmergencyContacts(testing=True)
contacts.database = DatabaseMock()

class TestEmergencyContacts_add(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/emergency_contacts/add'
        self.contacts = [
            {'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
            {'name': 'name2', 'email': 'email2', 'phone': 'phone2'},
            {'name': 'name3', 'email': 'email3', 'phone': 'phone3'}
        ]

    def tearDown(self):
        contacts.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_missing_required_data(self):
        data = {'foo': 'bar'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_user_not_exist(self):
        data = {'email': 'test_email', 'contacts': []}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_authenticated(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'contacts': []}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_error_in_contact_data(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        contacts.database.update_user('test_email', logged_in=True)
        contacts_list = [{'foo': 'bar'}]
        data = {'email': 'test_email', 'contacts': contacts_list}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='Required data missing in contacts list')

    def test_success(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        contacts.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email', 'contacts': self.contacts}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)


class TestEmergencyContacts_get(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/emergency_contacts/get'
        self.contacts = [
            {'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
            {'name': 'name2', 'email': 'email2', 'phone': 'phone2'},
            {'name': 'name3', 'email': 'email3', 'phone': 'phone3'}
        ]

    def tearDown(self):
        contacts.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_missing_required_data(self):
        data = {'foo': 'bar'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_user_not_exist(self):
        data = {'email': 'test_email'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_authenticated(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_success(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        contacts.database.update_user('test_email', logged_in=True)
        for contact in self.contacts:
            contacts.database.add_contact('test_system_id', contact['name'], contact['email'], contact['phone'])
        data = {'email': 'test_email'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=self.contacts)


class TestEmergencyContacts_update(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/emergency_contacts/update'
        self.contacts = [
            {'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
            {'name': 'name2', 'email': 'email2', 'phone': 'phone2'},
            {'name': 'name3', 'email': 'email3', 'phone': 'phone3'}
        ]

    def tearDown(self):
        contacts.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_missing_required_data(self):
        data = {'foo': 'bar'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_user_not_exist(self):
        data = {'email': 'test_email', 'contacts': []}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_authenticated(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'contacts': []}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_error_in_contact_data(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        contacts.database.update_user('test_email', logged_in=True)
        for contact in self.contacts:
            contacts.database.add_contact('test_system_id', contact['name'], contact['email'], contact['phone'])
        contacts_list = [{'foo': 'bar'}]
        data = {'email': 'test_email', 'contacts': contacts_list}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='Required data missing in contacts list')

    def test_success(self):
        contacts.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        contacts.database.update_user('test_email', logged_in=True)
        for contact in self.contacts:
            contacts.database.add_contact('test_system_id', contact['name'], contact['email'], contact['phone'])
        contacts_to_update = [
            {'name': 'name1', 'email': 'email4', 'phone': 'phone4'},
            {'name': 'name2', 'email': 'email5', 'phone': 'phone5'},
            {'name': 'name3', 'email': 'email6', 'phone': 'phone6'}
        ]
        data = {'email': 'test_email', 'contacts': contacts_to_update}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)