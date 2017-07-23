# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

from threading import Thread
import time
import hashlib
import imutils

from securityserverpy import _logger
from securityserverpy.sock import Sock
from securityserverpy.devices import DeviceManager
from securityserverpy.hwcontroller import HardwareController
from securityserverpy.config import Config
from securityserverpy.videostreamer import VideoStreamer


class SecurityServer(object):
    """handles server-client communication and processing of data sent and recieved"""

    # Constants
    _CONFIG_FILE = 'serverconfig.yaml.example'
    _DEFAULT_CAMERA1_ID = 0
    _DEFAULT_CAMERA2_ID = 1

    # Data expected to be recieved from clients
    _ARM_SYSTEM = 'ARMSYSTEM'
    _DISARM_SYSTEM = 'DISARMSYSTEM'
    _VIEW_CAMERA_FEED1 = 'VIEWCAMERAFEED1'
    _VIEW_CAMERA_FEED2 = 'VIEWCAMERAFEED2'
    _FALSE_ALARM = 'FALSEALARM'
    _CONTACT_DISPATCHER = 'CONTACTDISPATCHER'
    _NEWDEVICE = 'NEWDEVICE'
    _STOP_VIDEO_STREAM = 'STOPVIDEOSTREAM'

    # Data to be sent to clients
    _SUCCESS = 'SUCCESS'
    _FAILURE = 'FAILURE'

    def __init__(self, port):
        self.port = port
        self.sock = Sock(self.port)
        self.hwcontroller = HardwareController()
        self.device_manager = DeviceManager()
        self.security_config = Config(SecurityServer._CONFIG_FILE)
        self.videostream1 = VideoStreamer(camera=SecurityServer._DEFAULT_CAMERA1_ID)
        self.videostream2 = VideoStreamer(camera=SecurityServer._DEFAULT_CAMERA2_ID)

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
                args = (addr)
            else:
                args = (addr, True)
            server_thread = Thread(target=self._security_thread, args=args)
            server_thread.start()

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
        # Todo: status led on
        # Todo: Maybe lock doors if not already locked
        system_armed_thread = Thread(target=self._system_armed_thread, args=())
        system_armed_thread.start()

        return self.security_config.system_armed

    def _disarm_system(self):
        """disarms the security system

        returns:
            bool
        """
        self.security_config.system_armed = False
        if self.security_config.cameras_live:
            self.security_config.cameras_live = False
        # Todo: status led off
        # Todo: Maybe unlock doors if not already unlocked

        return not self.security_config.system_armed

    def _system_armed_thread(self):
        while self.security_config.system_armed:
            status1, _, motion_detected1 = self.videostream1.get_frame()
            status2, _, motion_detected2 = self.videostream2.get_frame()
            if status1 or status2:
                if motion_detected1 or motion_detected2:
                    # Send notification to client (System breach)
                    # Todo: status led flash
                    pass
            time.sleep(0.2)

    def _videostream_thread(self, stream):
        """thread for streaming video data to socket"""
        while self.security_config.cameras_live:
            status, data, _ = stream.get_frame()
            if status:
                self.sock.send_data(data)
            else:
                self.sock.send_data(SecurityServer._FAILURE)
            time.sleep(0.2)

    def _security_thread(self, addr, first_conn=False):
        """thread that constantly runs until `self.sock is stopped`

        Todo: see if we can use `self.sock.socket_listening` for the while loop case

        args:
            connection: socket.connection object
        """
        self.videostream1.start_stream()
        self.videostream2.start_stream()

        while True:
            if first_conn:
                first_conn = False
                self.sock.send_data(SecurityServer._NEWDEVICE)
                continue

            data = self.sock.recieve_data()

            if SecurityServer._NEWDEVICE in data:
                # Set device name
                device_name = data.split(':')[1]
                self._add_device(addr, device_name)
                self.sock.send_data(SecurityServer._SUCCESS)

            elif data == SecurityServer._DATA_ARM_SYSTEM:
                # arm system here
                armed = self._arm_system()
                if armed:
                    self.sock.send_data(SecurityServer._SUCCESS)
                else:
                    self.sock.send_data(SecurityServer._FAILURE)

            elif data == SecurityServer._DATA_DISARM_SYSTEM:
                # disarm system here
                disarmed = self._disarm_system()
                if disarmed:
                    self.sock.send_data(SecurityServer._SUCCESS)
                else:
                    self.sock.send_data(SecurityServer._FAILURE)

            elif data == SecurityServer._VIEW_CAMERA_FEED1:
                # live stream camera feed 1, if system is armed
                if not self.security_config.cameras_live:
                    self.security_config.cameras_live = True
                    stream_camera1_thread = Thread(target=self._videostream_thread, args=(self.videostream1))
                    stream_camera1_thread.start()

            elif data == SecurityServer._VIEW_CAMERA_FEED2:
                # live stream camera feed 2, if system is armed
                if not self.security_config.cameras_live:
                    self.security_config.cameras_live = True
                    stream_camera2_thread = Thread(target=self._videostream_thread, args=(self.videostream2))
                    stream_camera3_thread.start()

            elif data == SecurityServer._STOP_VIDEO_STREAM:
                if self.security_config.cameras_live:
                    self.security_config.cameras_live = False
                    self.sock.send_data(SecurityServer._SUCCESS)

            elif data == SecurityServer._CONTACT_DISPATCHER:
                # send message to dispatchers about break in
                pass
            elif data == SecurityServer._FALSE_ALARM:
                # system breach false alarm
                pass

        self.sock.close()
        self.security_config.store_config()
        self.device_manager.store_devices()
        if self.videostream1.stream_running:
            self.videostream1.stop_stream()
        if self.videostream2.stream_running:
            self.videostream2.stop_stream()
