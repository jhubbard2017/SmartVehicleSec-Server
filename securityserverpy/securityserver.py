# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import _thread
import time
import hashlib

from securityserverpy import _logger
from securityserverpy.sock import Sock

class SecurityData(object):
    """list of string constants for data that is expected to be sent to and recieved from clients"""

    def __init__(self):
        self.ARM_SYSTEM = 'ARMSYSTEM'
        self.DISARM_SYSTEM = 'DISARMSYSTEM'
        self.VIEW_CAMERA_FEED1 = 'VIEWCAMERAFEED1'
        self.VIEW_CAMERA_FEED2 = 'VIEWCAMERAFEED2'
        self.VIEW_CAMERA_FEED3 = 'VIEWCAMERAFEED3'
        self.RESPOND_OKAY = 'RESPONDOKAY'
        self.RESPOND_DISPATCHER = 'RESPONDDISPATCHER'
        self.DISCONNECTCLIENT = 'DISCONNECTCLIENT'


class SecurityServer(object):
    """handles server-client communication and processing of data sent and recieved"""

    def __init__(self, port):
        self.port = port
        self.sock = Sock(self.port)

    def start(self):
        """start the server to allow connections from incoming clients"""
        sock_success = self.sock.setup_socket()
        if sock_success:
            self._start_allowing_connections()

    def _start_allowing_connections(self):
        """listens for connections from incoming clients

        Upon recieving a succesful connection from a client, the server will start a new security thread
        for that connection

        Before starting the security thread, we want to do the following:
            - Todo: Check if device is in list of added and trustworthy devices (for security reasons)
            - If so, start thread
            - If not, do not start thread
        """
        while self.sock.socket_listening:
            connection = self.sock.accept()
            _thread.start_new_thread(self._serverthread, ())


    def _security_thread(self, connection):
        """thread that constantly runs until `self.sock is stopped`

        Todo: see if we can use `self.sock.socket_listening` for the while loop case

        args:
            connection: socket.connection object
        """
        sec_data = SecurityData()
        while True:
            data = self.sock.recieve_data()
            if data == sec_data.DATA_ARM_SYSTEM:
                # arm system here
                pass
            elif data == sec_data.DATA_DISARM_SYSTEM:
                # disarm system here
                pass
            elif data == sec_data.VIEW_CAMERA_FEED1:
                # live stream camera feed 1
                pass
            elif data == sec_data.VIEW_CAMERA_FEED2:
                # live stream camera feed 2
                pass
            elif data == sec_data.VIEW_CAMERA_FEED3:
                # live stream camera feed 1
                pass
            elif data == sec_data.RESPOND_DISPATCHER:
                # send message to dispatchers about break in
                pass
            elif data == sec_data.RESPOND_OKAY:
                # system breach false alarm
                pass
            elif data == sec_data.DISCONNECTCLIENT:
                break

