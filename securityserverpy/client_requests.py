# -*- coding: utf-8 -*-
#
# module for handling api request made to clients
#

import requests

from securityserverpy import _logger


class ClientRequests(object):
    """module for handling api request made to clients"""

    _SUCCESS_CODE = 201
    _FAILURE_CODE = 404

    def request(self, host, port, path, system_id, data={}):
        """Sends http request to ip address and port connection

        args:
            host: str
            port: str
            path: str
            rd_mac_address: str
            data: {}

        returns:
            json {}
        """
        url = 'http://{0}:{1}/system/{2}'.format(host, port, path)
        request_data = {'system_id': system_id}
        for key, value in data.iteritems():
            request_data[key] = value
        response = requests.post(url, json=request_data)
        if not response.json():
            return None

        return response.json()

    def make_request(self, host, port, system_id, path=None):
        """gets certain type of data from specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str
            path: str

        returns:
            {}
        """
        if not path:
            return None
        response = self.request(host, port, path, system_id)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return response['data']
