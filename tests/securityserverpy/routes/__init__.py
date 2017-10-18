# -*- coding: utf-8 -*-
#
# helpers for testing api calls
#

import json

class RestAPITestHelper(object):

    _STATUS_CODE = 200

    def __init__(self, app, test_class):
        self.app = app
        self.tester = test_class

    def check_reponse(self, response, expected_code, expected_data=None, expected_error=None):
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

    def post(self, path, data):
        """method to make a test post request to the testing server

        args:
            path: str
            data: {}

        returns:
            response object
        """
        return self.app.post(path, data=json.dumps(data), content_type='application/json', follow_redirects=True)