# -*- coding: utf-8 -*-
#
# module for testing RestAPI
#

import unittest
import json

from securityserverpy.flask.restapi import RestAPI
from tests.mocks.database_mock import DatabaseMock


_SUCCESS_CODE = 201
_FAILURE_CODE = 404
_NO_DATA_MESSAGE = 'No data found in request'
_EXPECTED_DATA_MISSING_MESSAGE = 'Expected data missing in request'

class RestAPITestHelper(object):
    """helper class for testing RestAPI calls"""

    _STATUS_CODE = 200

    def __init__(self, app, tester):
        self.app = app
        self.tester = tester

    def get_security_config(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/security_config', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def add_new_device(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/add_new_device', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def add_contacts(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/add_contacts', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def update_contacts(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/update_contacts', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def get_contacts(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/get_contacts', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def remove_device(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/remove_device', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def get_device_info(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/get_device_info', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def update_device_info(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/update_device_info', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def get_md_device(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/get_md_device', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def get_rd_device(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/get_rd_device', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def arm_system(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/arm', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def disarm_system(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/disarm', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def get_logs(self, data, expected_code, expected_data=None, expected_error=None):
        response = self._post('/system/logs', data)
        self._check_reponse(response, expected_code, expected_data, expected_error)

    def set_false_alarm(self, data, expected_code, expected_data):
        response = self._post('/system/false_alarm', data)
        self._check_reponse(response, expected_code, expected_data)

    def get_location_coordinates(self, data, expected_code, expected_data):
        response = self._post('/system/location', data)
        self._check_reponse(response, expected_code, expected_data)

    def get_temperature(self, data, expected_code, expected_data):
        response = self._post('/system/temperature', data)
        self._check_reponse(response, expected_code, expected_data)

    def get_speedometer_data(self, data, expected_code, expected_data):
        response = self._post('/system/speedometer', data)
        self._check_reponse(response, expected_code, expected_data)

    def create_securityconfig(self, data, expected_code, expected_data):
        response = self._post('/system/create_securityconfig', data)
        self._check_reponse(response, expected_code, expected_data)

    def add_connection(self, data, expected_code, expected_data):
        response = self._post('/system/add_connection', data)
        self._check_reponse(response, expected_code, expected_data)

    def update_connection(self, data, expected_code, expected_data):
        response = self._post('/system/update_connection', data)
        self._check_reponse(response, expected_code, expected_data)

    def set_system_breached(self, data, expected_code, expected_data):
        response = self._post('/system/set_breached', data)
        self._check_reponse(response, expected_code, expected_data)

    def get_connection(self, data, expected_code, expected_data):
        response = self._post('/system/get_connection', data)
        self._check_reponse(response, expected_code, expected_data)

    def panic_response(self, data, expected_code, expected_data):
        response = self._post('/system/panic', data)
        self._check_reponse(response, expected_code, expected_data)

    def _check_reponse(self, response, expected_code, expected_data=None, expected_error=None):
        json_data = json.loads(response.data)
        self.tester.assertEqual(response.status_code, self._STATUS_CODE)
        self.tester.assertEqual(json_data['code'], expected_code)
        if expected_data:
            if type(expected_data) is list:
                data_list = json_data['data']
                for data in expected_data:
                    self.tester.assertTrue(data, data_list)
            else:
                self.tester.assertEqual(json_data['data'], expected_data)
        if expected_error:
            self.tester.assertEqual(json_data['message'], expected_error)

    def _post(self, path, data):
        """method to make a test post request to the testing server

        args:
            path: str
            data: {}

        returns:
            response object
        """
        return self.app.post(path, data=json.dumps(data), content_type='application/json', follow_redirects=True)


class TestRestAPI_get_security_config(unittest.TestCase):
    """class for testing get_security_config in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.get_security_config(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.get_security_config(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_rdevice_not_exist(self):
        data = {'md_mac_address': 'foo'}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to get client id'
        self.helper.get_security_config(data, expected_code, expected_error=expected_error)

    def test_config_not_exist(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        data = {'rd_mac_address': 'rd_test_device'}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to get security config from server'
        self.helper.get_security_config(data, expected_code, expected_error=expected_error)

    def test_success(self):
        # Add neccessary data
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        self.restapi.database.add_security_config('rd_test_device')

        data = {'md_mac_address': 'md_test_device'}
        expected_code = _SUCCESS_CODE
        expected_data = {'system_armed': False, 'system_breached': False}
        self.helper.get_security_config(data, expected_code, expected_data=expected_data)


class TestRestAPI_add_contacts(unittest.TestCase):
    """class for testing add_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.add_contacts(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.add_contacts(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_rdevice_not_exist(self):
        data = {'md_mac_address': 'foo', 'contacts': []}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to get client from server'
        self.helper.add_contacts(data, expected_code, expected_error=expected_error)

    def test_database_failure(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        self.restapi.database.add_side_effect()
        contacts = [{'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
                    {'name': 'name2', 'email': 'email2', 'phone': 'phone2'}]
        data = {'md_mac_address': 'md_test_device', 'contacts': contacts}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to add contact recipients'
        self.helper.add_contacts(data, expected_code, expected_error=expected_error)

    def test_success(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        contacts = [{'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
                    {'name': 'name2', 'email': 'email2', 'phone': 'phone2'}]
        data = {'md_mac_address': 'md_test_device', 'contacts': contacts}
        expected_code = _SUCCESS_CODE
        expected_data = True
        self.helper.add_contacts(data, expected_code, expected_data=expected_data)

        saved_contacts = self.restapi.database.get_contacts('rd_test_device')
        for contact in saved_contacts:
            self.assertTrue(contact in contacts)


class TestRestAPI_update_contacts(unittest.TestCase):
    """class for testing update_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.update_contacts(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.update_contacts(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_rdevice_not_exist(self):
        data = {'md_mac_address': 'foo', 'contacts': []}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to get client from server'
        self.helper.update_contacts(data, expected_code, expected_error=expected_error)

    def test_database_failure(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        self.restapi.database.add_side_effect()
        contacts = [{'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
                    {'name': 'name2', 'email': 'email2', 'phone': 'phone2'}]
        data = {'md_mac_address': 'md_test_device', 'contacts': contacts}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to remove current contact recipients'
        self.helper.update_contacts(data, expected_code, expected_error=expected_error)

    def test_success(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        contacts = [{'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
                    {'name': 'name2', 'email': 'email2', 'phone': 'phone2'}]
        for contact in contacts:
            self.restapi.database.add_contact('rd_test_device', contact['name'], contact['email'], contact['phone'])

        updated_contacts = [{'name': 'name1', 'email': 'email3', 'phone': 'phone3'},
                            {'name': 'name2', 'email': 'email4', 'phone': 'phone4'}]
        data = {'md_mac_address': 'md_test_device', 'contacts': updated_contacts}
        expected_code = _SUCCESS_CODE
        expected_data = True
        self.helper.update_contacts(data, expected_code, expected_data=expected_data)

        # Check if contacts were updated
        contacts = self.restapi.database.get_contacts('rd_test_device')
        for contact in contacts:
            self.assertTrue(contact in updated_contacts)


class TestRestAPI_get_contacts(unittest.TestCase):
    """class for testing get_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.get_contacts(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.get_contacts(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_rdevice_not_exist(self):
        data = {'md_mac_address': 'foo'}
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to get client from server'
        self.helper.get_contacts(data, expected_code, expected_error=expected_error)

    def test_contacts_not_exist(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        data = {'md_mac_address': 'md_test_device'}
        expected_code = _SUCCESS_CODE
        expected_data = {'contacts_exist': False}
        self.helper.get_contacts(data, expected_code, expected_data=expected_data)

    def test_success(self):
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        contacts = [{'name': 'name1', 'email': 'email1', 'phone': 'phone1'},
                    {'name': 'name2', 'email': 'email2', 'phone': 'phone2'}]
        for contact in contacts:
            self.restapi.database.add_contact('rd_test_device', contact['name'], contact['email'], contact['phone'])

        data = {'md_mac_address': 'md_test_device'}
        expected_code = _SUCCESS_CODE
        expected_data = contacts
        self.helper.get_contacts(data, expected_code, expected_data=expected_data)


class TestRestAPI_add_new_device(unittest.TestCase):
    """class for testing add_new_device in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.add_new_device(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.add_new_device(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_add_mobile_device_database_error(self):
        self.restapi.database.add_mobile_device_side_effect = True
        data = {
            'md_mac_address': 'foo',
            'name': 'name1',
            'email': 'email2',
            'phone': 'phone2',
            'vehicle': 'c2',
            'rd_mac_address': 'bar'
        }
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to add device to server'
        self.helper.add_new_device(data, expected_code, expected_error=expected_error)

    def test_add_rd_device_database_error(self):
        self.restapi.database.add_raspberry_pi_device_side_effect = True
        data = {
            'md_mac_address': 'foo',
            'name': 'name1',
            'email': 'email2',
            'phone': 'phone2',
            'vehicle': 'c2',
            'rd_mac_address': 'bar'
        }
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to add security system to server'
        self.helper.add_new_device(data, expected_code, expected_error=expected_error)

    def test_success(self):
        data = {
            'md_mac_address': 'foo',
            'name': 'name1',
            'email': 'email2',
            'phone': 'phone2',
            'vehicle': 'c2',
            'rd_mac_address': 'bar'
        }
        expected_code = _SUCCESS_CODE
        expected_data = True
        self.helper.add_new_device(data, expected_code, expected_data=expected_data)


class TestRestAPI_remove_md_device(unittest.TestCase):
    """class for testing remove_md_device in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.remove_device(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.remove_device(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_rdevice_not_exist(self):
        data = {'md_mac_address': 'foo'}
        expected_code = _FAILURE_CODE
        expected_error = 'Error getting security system id'
        self.helper.remove_device(data, expected_code, expected_error=expected_error)

    def test_remove_md_device_database_error(self):
        self.restapi.database.add_mobile_device('md_test_device', 'n1', 'e1', 'p1', 'v1')
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        self.restapi.database.remove_mobile_device_side_effect = True
        data = {'md_mac_address': 'md_test_device'}
        expected_code = _FAILURE_CODE
        expected_error = 'Error removing mobile device'
        self.helper.remove_device(data, expected_code, expected_error=expected_error)

    def test_remove_raspberrypi_device_database_error(self):
        self.restapi.database.add_mobile_device('md_test_device', 'n1', 'e1', 'p1', 'v1')
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        self.restapi.database.remove_raspberry_pi_device_side_effect = True
        data = {'md_mac_address': 'md_test_device'}
        expected_code = _FAILURE_CODE
        expected_error = 'Error removing system from server'
        self.helper.remove_device(data, expected_code, expected_error=expected_error)

    def test_success(self):
        self.restapi.database.add_mobile_device('md_test_device', 'n1', 'e1', 'p1', 'v1')
        self.restapi.database.add_raspberry_pi_device('md_test_device', 'rd_test_device')
        data = {'md_mac_address': 'md_test_device'}
        expected_code = _SUCCESS_CODE
        expected_data = True
        self.helper.remove_device(data, expected_code, expected_data=expected_data)


class TestRestAPI_update_device_info(unittest.TestCase):
    """class for testing update_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.update_device_info(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.update_device_info(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)

    def test_database_error(self):
        data = {
            'md_mac_address': 'foo',
            'name': 'name1',
            'email': 'email2',
            'phone': 'phone2',
            'vehicle': 'c2'
        }
        expected_code = _FAILURE_CODE
        expected_error = 'Failed to update device information'
        self.helper.update_device_info(data, expected_code, expected_error=expected_error)

    def test_success(self):
        self.restapi.database.add_mobile_device('md_test_device', 'n1', 'e1', 'p1', 'v1')
        data = {
            'md_mac_address': 'md_test_device',
            'name': 'name1',
            'email': 'email2',
            'phone': 'phone2',
            'vehicle': 'c2'
        }
        expected_code = _SUCCESS_CODE
        expected_data = True
        self.helper.update_device_info(data, expected_code, expected_data=expected_data)

        del data['md_mac_address']
        saved_data = self.restapi.database.get_mobile_device_information('md_test_device')
        self.assertEqual(saved_data, data)


class TestRestAPI_get_device(unittest.TestCase):
    """class for testing update_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.get_md_device(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.get_md_device(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)


class TestRestAPI_get_rd_device(unittest.TestCase):
    """class for testing update_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()

    def test_no_data(self):
        data = {}
        expected_code = _FAILURE_CODE
        self.helper.get_rd_device(data, expected_code, expected_error=_NO_DATA_MESSAGE)

    def test_wrong_data(self):
        data = {'hello': 'world'}
        expected_code = _FAILURE_CODE
        self.helper.get_rd_device(data, expected_code, expected_error=_EXPECTED_DATA_MISSING_MESSAGE)


class TestRestAPI_arm_system(unittest.TestCase):
    """class for testing update_contacts in RestAPI"""

    def setUp(self):
        self.restapi = RestAPI('127.0.0.1', 3001, testing=True, dev=False)
        self.restapi.database = DatabaseMock()
        app = self.restapi.flask_app().test_client()
        self.helper = RestAPITestHelper(app, tester=self)

    def tearDown(self):
        self.restapi.database.clear_all_tables()
