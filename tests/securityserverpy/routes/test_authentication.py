# -*- coding: utf-8 -*-
#
# module for testing authentication
#

import unittest
import json

from securityserverpy.routes.authentication import Authentication
from tests.mocks.database_mock import DatabaseMock
from securityserverpy.routes import app, _FAILURE_CODE, _SUCCESS_CODE
from securityserverpy.routes import _NO_DATA_MESSAGE, _EXPECTED_DATA_MISSING_MESSAGE
from tests.securityserverpy.routes import RestAPITestHelper

authentication = Authentication(testing=True)
authentication.database = DatabaseMock()

class TestAuthentication_login(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/authentication/login'

    def tearDown(self):
        authentication.database.clear_all_tables()

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
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_already_logged_in(self):
        authentication.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        authentication.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User already logged in')

    def test_success(self):
        authentication.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)

class TestAuthentication_logout(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/authentication/logout'

    def tearDown(self):
        authentication.database.clear_all_tables()

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
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_logged_in(self):
        authentication.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not logged in')

    def test_success(self):
        authentication.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        authentication.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email', 'password': 'test_password'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)