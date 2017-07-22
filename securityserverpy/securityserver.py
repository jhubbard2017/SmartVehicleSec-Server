# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import _thread
import time
import hashlib

from securityserverpy import _logger
from securityserverpy.sock import Sock
from securityserverpy.devices import DeviceManager
from securityserverpy.hwcontroller import HardwareController
from securityserverpy.config import Config

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
        self.NEWDEVICE = 'NEWDEVICE'
        self.SUCCESS = 'SUCCESS'
        self.FAIL = 'FAIL'


class SecurityServer(object):
    """handles server-client communication and processing of data sent and recieved"""

    _CONFIG_FILE = 'serverconfig.yaml.example'

    def __init__(self, port):
        self.port = port
        self.sock = Sock(self.port)
        self.hwcontroller = HardwareController()
        self.device_manager = DeviceManager()

        self.security_config = Config(SecurityServer._CONFIG_FILE)

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
            connection, addr = self.sock.accept()
            if self.device_manager.device_exist(addr):
                _thread.start_new_thread(self._serverthread, (addr,))
            else:
                _thread.start_new_thread(self._security_thread, (addr, True))

    def _add_device(self, addr, name):
        """adds a new device to list of allowed devices

        We only add the device if its not already in the device manager

        args:
            addr: str

        returns:
            bool
        """
        already_exist = self.device_manager.device_exist(addr)
        if not already_exist:
            self.device_manager.add_device(addr, name)
        return already_exist

    def _arm_system(self):
        """arms the security system

        returns:
            bool
        """
        self.security_config.system_armed = True
        # Todo: Start camera livestreams
        # Todo: Maybe lock doors if not already locked
        return self.security_config.system_armed

    def _disarm_system(self):
        """disarms the security system

        returns:
            bool
        """
        self.security_config.system_armed = False
        # Todo: Stop camera streams
        # Todo: Maybe unlock doors if not already unlocked
        return not self.security_config.system_armed

    def _security_thread(self, addr, first_conn=False):
        """thread that constantly runs until `self.sock is stopped`

        Todo: see if we can use `self.sock.socket_listening` for the while loop case

        args:
            connection: socket.connection object
        """
        sec_data = SecurityData()
        while True:
            if first_conn:
                first_conn = False
                self.sock.send_data(sec_data.NEWDEVICE)
                continue

            data = self.sock.recieve_data()

            if sec_data.NEWDEVICE in data:
                # Set device name
                device_name = data.split(':')[1]
                self._add_device(addr, device_name)
                self.sock.send_data(sec_data.SUCCESS)

            elif data == sec_data.DATA_ARM_SYSTEM:
                # arm system here
                armed = self._arm_system()
                if armed:
                    self.sock.send_data(sec_data.SUCCESS)
                else:
                    self.sock.send_data(sec_data.FAIL)

            elif data == sec_data.DATA_DISARM_SYSTEM:
                # disarm system here
                disarmed = self._disarm_system()
                if disarmed:
                    self.sock.send_data(sec_data.SUCCESS)
                else:
                    self.sock.send_data(sec_data.FAIL)

            elif data == sec_data.VIEW_CAMERA_FEED1:
                # live stream camera feed 1, if system is armed
                pass
            elif data == sec_data.VIEW_CAMERA_FEED2:
                # live stream camera feed 2, if system is armed
                pass
            elif data == sec_data.VIEW_CAMERA_FEED3:
                # live stream camera feed 1, if system is armed
                pass
            elif data == sec_data.RESPOND_DISPATCHER:
                # send message to dispatchers about break in
                pass
            elif data == sec_data.RESPOND_OKAY:
                # system breach false alarm
                pass
            elif data == sec_data.DISCONNECTCLIENT:
                break

