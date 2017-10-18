# -*- coding: utf-8 -*-
#
# module for testing connections
#

import unittest
import json

from securityserverpy.routes.connections import Connections
from tests.mocks.database_mock import DatabaseMock
from securityserverpy.routes import app, _FAILURE_CODE, _SUCCESS_CODE
from securityserverpy.routes import _NO_DATA_MESSAGE, _EXPECTED_DATA_MISSING_MESSAGE
from tests.securityserverpy.routes import RestAPITestHelper

connections = Connections(testing=True)
connections.database = DatabaseMock()

class TestConnections_add(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/connections/add'

    def tearDown(self):
        connections.database.clear_all_tables()

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

    def test_connection_already_exist(self):
        connections.database.add_connection('test_system_id', 'test_host', 'test_port')
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='Connection already exist')

    def test_success(self):
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)


class TestConnections_get(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/connections/get'

    def tearDown(self):
        connections.database.clear_all_tables()

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

    def test_success_connection_not_exist(self):
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=False)

    def test_success_connection_exist(self):
        connections.database.add_connection('test_system_id', 'test_host', 'test_port')
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _SUCCESS_CODE
        expected_data = {'host': 'test_host', 'port': 'test_port'}
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=expected_data)


class TestConnections_update(unittest.TestCase):

    def setUp(self):
        self.helper = RestAPITestHelper(app.test_client(), test_class=self)
        self.path = '/connections/update'

    def tearDown(self):
        connections.database.clear_all_tables()

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

    def test_connection_not_exist(self):
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _FAILURE_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_error='Connection does not exist')

    def test_success(self):
        connections.database.add_connection('test_system_id', 'test_host', 'test_port')
        data = {'system_id': 'test_system_id', 'host': 'test_host', 'port': 'test_port'}
        expected_code = _SUCCESS_CODE
        reponse = self.helper.post(self.path, data)
        self.helper.check_reponse(reponse, expected_code, expected_data=True)