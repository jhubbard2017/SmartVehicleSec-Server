# -*- coding: utf-8 -*-
#
# error handling for flask
#

from securityserverpy import _logger

class FlaskErrorHandling(object):

    def __init__(self):
        pass

    def _check_json_for_error(self, json, keys, all_should_exist):
        """checks if keys are located in a json object

        args:
            json: {}
            keys: [str]

        returns:
            bool, str
        """
        error_found = True
        if not json:
            error_message = 'No data found in request'
            return error_found, error_message

        if all_should_exist:
            for key in keys:
                if not key in json:
                    error_message = 'Expected data missing in request'
                    return error_found, error_message
        else:
            no_keys_found = True
            for key in keys:
                if key in json:
                    no_keys_found = False
                    break

            if no_keys_found:
                error_message = 'No device found in request'
                return error_found, error_message

        return not error_found, None

    def check_system_request(self, json, keys, all_should_exists=False):
        """checks the get security config request for errors

        returns:
            status, error
        """
        error_found = True
        error_found, error = self._check_json_for_error(json, keys, all_should_exists)
        if error_found:
            return error_found, error

        return not error_found, None
