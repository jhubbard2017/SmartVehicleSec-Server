# -*- coding: utf-8 -*-
#
# module for testing APIErrorHandling
#

import unittest

from securityserverpy.flask.error_handling import APIErrorHandling

_NO_DATA_MESSAGE = 'No data found in request'
_EXPECTED_DATA_MISSING_MESSAGE = 'Expected data missing in request'


class TestAPIErrorHandling_CheckJSON(unittest.TestCase):
    """class for testing _check_json method in APIErrorHandling"""

    def setUp(self):
        """setup test before each test case"""
        self.error_handling = APIErrorHandling()
        self.json = {'hello': 'world', 'foo': 'bar'}
        self.keys = ['hello', 'foo']

    def tearDown(self):
        """clean up after each test case"""
        pass

    def _check_json_results(self, json, keys, all_should_exist, expected_status, expected_error):
        status, error = self.error_handling._check_json(json, keys, all_should_exist)
        self.assertEqual(status, expected_status)
        self.assertEqual(error, expected_error)

    def test_empty_json(self):
        self.json = {}
        self._check_json_results(
            self.json, self.keys, all_should_exist=False, expected_status=False, expected_error=_NO_DATA_MESSAGE
        )

    def test_keys_exist_with_all_should_exist(self):
        self._check_json_results(self.json, self.keys, all_should_exist=True, expected_status=True, expected_error=None)

    def test_keys_not_exist_with_all_should_exist(self):
        del self.json['hello']
        self._check_json_results(
            self.json, self.keys, all_should_exist=True, expected_status=False, expected_error=_EXPECTED_DATA_MISSING_MESSAGE
        )

    def test_key_exist_with_all_should_not_exist(self):
        del self.json['hello']
        self._check_json_results(self.json, self.keys, all_should_exist=False, expected_status=True, expected_error=None)

    def test_keys_not_exist_with_all_should_not_exist(self):
        self.json = {'new': 'key'}
        self._check_json_results(
            self.json, self.keys, all_should_exist=False, expected_status=False, expected_error=_EXPECTED_DATA_MISSING_MESSAGE
        )


class TestAPIErrorHandling_CheckSystemRequest(unittest.TestCase):
    """class for testing check_system_request method in APIErrorHandling"""

    def setUp(self):
        """setup test before each test case"""
        self.error_handling = APIErrorHandling()
        self.json = {'hello': 'world', 'foo': 'bar'}
        self.keys = ['hello', 'foo']

    def test_check_json_success(self):
        status, error = self.error_handling.check_system_request(self.json, self.keys, all_should_exist=True)
        self.assertTrue(status)
        self.assertIsNone(error)

    def test_check_json_failure(self):
        del self.json['hello']
        status, error = self.error_handling.check_system_request(self.json, self.keys, all_should_exist=True)
        self.assertFalse(status)
        self.assertEqual(error, _EXPECTED_DATA_MISSING_MESSAGE)
