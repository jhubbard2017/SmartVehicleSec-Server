# -*- coding: utf-8 -*-
#
# module for testing users
#

import unittest
import json
from mock import Mock

from securityserverpy.routes.users import Users
from tests.mocks.database_mock import DatabaseMock
from securityserverpy.routes import app, _FAILURE_CODE, _SUCCESS_CODE
from securityserverpy.routes import _NO_DATA_MESSAGE, _EXPECTED_DATA_MISSING_MESSAGE
from tests.securityserverpy.routes import RestAPITestHelper

users = Users(testing=True)
users.database = DatabaseMock()

class TestUsers_add(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/users/add'

    def tearDown(self):
        users.database.clear_all_tables()

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

    def test_user_already_exist(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {
            'email': 'test_email', 'password': 'test_password', 'firstname': 'test_firstname',
            'lastname': 'test_lastname', 'phone': 'test_phone', 'vehicle': 'test_vehicle', 'system_id': 'test_system_id'
        }
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User already exist')

    def test_success(self):
        data = {
            'email': 'test_email', 'password': 'test_password', 'firstname': 'test_firstname',
            'lastname': 'test_lastname', 'phone': 'test_phone', 'vehicle': 'test_vehicle', 'system_id': 'test_system_id'
        }
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)


class TestUsers_get(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/users/get'

    def tearDown(self):
        users.database.clear_all_tables()

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
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_success(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        users.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email'}
        expected_code = _SUCCESS_CODE
        expected_data = {
            'email': 'test_email', 'password': 'test_password', 'firstname': 'test_firstname',
            'lastname': 'test_lastname', 'phone': 'test_phone', 'vehicle': 'test_vehicle', 'system_id': 'test_system_id', 'logged_in': True
        }
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=expected_data)


class TestUsers_remove(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/users/remove'

    def tearDown(self):
        users.database.clear_all_tables()

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
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_success(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        users.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)


class TestUsers_update(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/users/update'

    def tearDown(self):
        users.database.clear_all_tables()

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
        data = {
            'email': 'test_email', 'firstname': 'test_firstname2', 'lastname': 'test_lastname2',
            'phone': 'test_phone2', 'vehicle': 'test_vehicle2', 'system_id': 'test_system_id2'
        }
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_authenticated(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {
            'email': 'test_email', 'firstname': 'test_firstname2', 'lastname': 'test_lastname2',
            'phone': 'test_phone2', 'vehicle': 'test_vehicle2', 'system_id': 'test_system_id2'
        }
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_success(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        users.database.update_user('test_email', logged_in=True)
        data = {
            'email': 'test_email', 'firstname': 'test_firstname2', 'lastname': 'test_lastname2',
            'phone': 'test_phone2', 'vehicle': 'test_vehicle2', 'system_id': 'test_system_id2'
        }
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)


class TestUsers_change_password(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/users/change_password'

    def tearDown(self):
        users.database.clear_all_tables()

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
        data = {'email': 'test_email', 'old_password': 'test_old_password', 'new_password': 'test_new_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_incorrect_password(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'old_password': 'test_old_password', 'new_password': 'test_new_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User does not exist')

    def test_user_not_authenticated(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        data = {'email': 'test_email', 'old_password': 'test_password', 'new_password': 'test_new_password'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='User not authenticated')

    def test_success(self):
        users.database.add_user('test_email', 'test_password', 'test_firstname', 'test_lastname', 'test_phone', 'test_vehicle', 'test_system_id')
        users.database.update_user('test_email', logged_in=True)
        data = {'email': 'test_email', 'old_password': 'test_password', 'new_password': 'test_new_password'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)
