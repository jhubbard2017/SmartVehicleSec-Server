# -*- coding: utf-8 -*-
#
# module for controller server connections and communications
#

import socket
import sys

from securityserverpy import _logger


class Sock(object):
    """ controls communication to and from connected clients.

    This module is designed to connect to clients, send and recieve data, and close connections when desired.

    Upon creation of a `Sock` object, the socket is automatically binded to the assigned host and port and
    listening automatically begins.

        - This decreases the amount of code needed by the user of this class to start up the socket, bind it, and
          start the listening process.

        - a byte size of 1024 is the limit for the amount of data that can be sent per network round trip.

        - a listening timeout of 5 tries is set for listening/establishing communication
    """

    _SERVER_LISTEN_TIMEOUT = 5
    _SERVER_RECV_BYTES = 1024
    _DEFAULT_PORT = 2200

    def __init__(self, port=None):
        self._port = port or Sock._DEFAULT_PORT
        self._host = socket.gethostbyname('localhost')      # socket.gethostbyname(socket.getfqdn())
        self._socket = socket.socket()
        self._socket_listening = False
        self._connection = None
        self._connected_addr = None

    def setup_socket(self):
        """binds the host and port to the socket"""
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._socket.bind((self._host, self._port))
        except socket.error as error:
            _logger.error('Socket binding failed: code[{0}] message[{1}]'.format(error[0], error[1]))
            return False

        _logger.debug('Socket set up successful')

        # allows socket to start listening for incoming connection request
        self._socket.listen(Sock._SERVER_LISTEN_TIMEOUT)
        self._socket_listening = True
        _logger.debug('Socket listening to port[{0}]'.format(self._port))

        return True

    def accept(self):
        """accepts a connection from a client

        returns:
            socket.connection object
        """
        self._connection, self._connected_addr = self._socket.accept()
        _logger.debug('Recieving connection: address[{0}]'.format(self._connected_addr[0]))
        return self._connection, self._connected_addr

    def close(self):
        """ends the socket connection"""
        self._socket_listening = False
        self._connection.close()
        _logger.debug('Socket stopped. Binding removed.')

    def recieve_data(self):
        """fetches and returns data sent to server from client

        returns:
            str
        """
        cdata = None
        data = self._connection.recv(Sock._SERVER_RECV_BYTES)
        if not data:
            _logger.debug('No data received from client.')
            return cdata

        cdata = bytes(data).decode().replace('\r\n', '')
        return cdata

    def send_data(self, data):
        """sends data to sock to be retrieved by client

        args:
            data: str

        returns:
            bool
        """
        data = data.encode()
        try:
            self._connection.send(data)
        except socket.error as error:
            return False

        return True

    # Getter methods for needed attributes outside of class level
    @property
    def connection(self):
        return self._connection

    @property
    def socket_listening(self):
        return self._socket_listening

    @property
    def host(self):
        return self._host

    @property
    def connected_addr(self):
        return self._connected_addr