# -*- coding: utf-8 -*-
#
# Useful objects and methods for routes
#

from flask import Flask, jsonify
from securityserverpy import _logger
from securityserverpy.database.database import Database

# Neccessary constants
_SUCCESS_CODE = 201
_FAILURE_CODE = 404
_NO_DATA_MESSAGE = 'No data found in request'
_EXPECTED_DATA_MISSING_MESSAGE = 'Expected data missing in request'

# Flask and database init
app = Flask(__name__)
database = Database()

# Methods
def error_response(error, user_system='Unknown'):
    """error handler for FLASK API calls

    args:
        message: str

    returns:
        jsonify({code, data, message})
    """
    _logger.info('Aborting with error: [{0}] for user/system [{1}]'.format(error, user_system))
    return jsonify({'code': _FAILURE_CODE, 'message': error})

def success_response(path, data=True):
    """success handler method for FLASK API calls

    args:
        message: str
        data: {}/bool

    returns:
        jsonify()
    """
    _logger.debug('Success! Sending data for path [{0}] data [{1}]'.format(path, data))
    return jsonify({'code': _SUCCESS_CODE, 'data': data})


def verify_request(json, keys, all_should_exist):
    """checks if keys are located in a json object

    args:
        json: {}
        keys: [str]

    returns:
        bool, str
    """
    if not json:
        return (False, _NO_DATA_MESSAGE)

    if all_should_exist:
        for key in keys:
            if not key in json:
                return (False, _EXPECTED_DATA_MISSING_MESSAGE)
    else:
        one_expected_key_found = False
        for key in keys:
            if key in json:
                one_expected_key_found = True
                break
        if not one_expected_key_found:
            return (False, _EXPECTED_DATA_MISSING_MESSAGE)

    return (True, None)
