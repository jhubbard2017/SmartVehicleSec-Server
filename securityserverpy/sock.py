# -*- coding: utf-8 -*-
#
# module for controller server connections and communications
#

import socket
import sys

from securityserverpy import _logger


class UDPSock(object):
    """ controls communication to and from connected clients.

    This module is designed to connect to clients, send and recieve data, and close connections when desired.

    Upon creation of a `Sock` object, the socket is automatically binded to the assigned host and port and
    listening automatically begins.

        - This decreases the amount of code needed by the user of this class to start up the socket, bind it, and
          start the listening process.

        - a byte size of 1024 is the limit for the amount of data that can be sent per network round trip.

        - a listening timeout of 5 tries is set for listening/establishing communication
    """

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.client = (ip, port)

    def send_data(self, data):
        """sends data to sock to be retrieved by client"""
        self.sock.sendto(data, self.client)
