# -*- coding: utf-8 -*-
#
# module for handling errors made during rest api calls from clients
#

from securityserverpy import _logger


class APIErrorHandling(object):

    _NO_DATA_MESSAGE = 'No data found in request'
    _EXPECTED_DATA_MISSING_MESSAGE = 'Expected data missing in request'

    def _check_json(self, json, keys, all_should_exist):
        """checks if keys are located in a json object

        args:
            json: {}
            keys: [str]

        returns:
            bool, str
        """
        if not json:
            return (False, self._NO_DATA_MESSAGE)

        if all_should_exist:
            for key in keys:
                if not key in json:
                    return (False, self._EXPECTED_DATA_MISSING_MESSAGE)
        else:
            one_expected_key_found = False
            for key in keys:
                if key in json:
                    one_expected_key_found = True
                    break
            if not one_expected_key_found:
                return (False, self._EXPECTED_DATA_MISSING_MESSAGE)

        return (True, None)

    def check_system_request(self, json, keys, all_should_exist=False):
        """checks the get security config request for errors

        args:
            json: {}
            keys: []
            all_should_exist: bool

        returns:
            bool, str
        """
        status, error = self._check_json(json, keys, all_should_exist)
        if not status:
            return (False, error)

        return (True, None)
