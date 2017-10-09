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

    def request(self, host, port, path, rd_mac_address, data={}):
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
        request_data = {'rd_mac_address': rd_mac_address}
        for key, value in data.iteritems():
            request_data[key] = value
        response = requests.post(url, json=request_data)
        if not response.json():
            return None

        return response.json()

    def arm(self, host, port, rd_mac_address):
        """arms a security system at a specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str

        returns:
            bool
        """
        path = 'arm'
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return True

    def disarm(self, host, port, rd_mac_address):
        """disarms a security system at a specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str

        returns:
            bool
        """
        path = 'disarm'
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return True

    def false_alarm(self, host, port, rd_mac_address):
        """sets security breach as false alarm at a specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str

        returns:
            bool
        """
        path = 'false_alarm'
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return True

    def location(self, host, port, rd_mac_address):
        """gets gps coordinates at a specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str

        returns:
            {}
        """
        path = 'location'
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return response['data']

    def get_data(self, host, port, rd_mac_address, path=None):
        """gets certain type of data from specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str
            type: str

        returns:
            {}
        """
        if not path:
            return None
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return response['data']


    def temperature(self, host, port, rd_mac_address):
        """gets temperature data at a specific host and port

        args:
            host: str
            port: str
            rd_mac_address: str

        returns:
            bool
        """
        path = 'temperature'
        response = self.request(host, port, path, rd_mac_address)
        if not response or response['code'] == self._FAILURE_CODE:
            return False

        return response['data']

