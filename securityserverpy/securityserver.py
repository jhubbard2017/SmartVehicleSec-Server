# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

from threading import Thread
import time
import hashlib
import imutils
import datetime

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
    _NEWDEVICE = 'NEWDEVICE'
    _STOP_VIDEO_STREAM = 'STOPVIDEOSTREAM'
    _DISCONNECT = 'DISCONNECT'

    # Data to be sent to clients
    _SUCCESS = 'SUCCESS'
    _FAILURE = 'FAILURE'
    _SYSTEM_BREACHED = 'SYSTEMBREACHED'

    # status LED flash signals
    _FLASH_NEW_DEVICE = 3
    _FLASH_SYSTEM_ARMED = 10
    _FLASH_SYSTEM_DISARMED = 5
    _FLASH_DEVICE_CONNECTED = 4
    _FLASH_SERVER_ON = 3

    def __init__(self, port=None, host=None, no_hardare=None):
        """constructor method for SecurityServer

        HardwareController: used to control all pieces of hardware connected to the raspberry pi
        DeviceManager: module used to store device information that connects to the server
        SecurityConfig: a collection of security attributes about the system (system armed, cameras live, etc.)
        VideoStreamer: module to control video streaming to clients from server, and motion detection
        """
        self.port = port
        self.host = host
        self.sock = Sock(port=self.port, host=self.host)
        self.device_manager = DeviceManager()
        self.security_config = Config(SecurityServer._CONFIG_FILE)

        self.no_hardware = no_hardare or False
        if not self.no_hardware:
            self.hwcontroller = HardwareController()
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
        if not self.no_hardware:
            self.videostream1.start_stream()
            _logger.debug('Started video stream.')

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
            if not self.no_hardware:
                self.hwcontroller.status_led_flash(SecurityServer._FLASH_NEW_DEVICE)
        return already_exist

    def _arm_system(self):
        """arms the security system

        In this process, the things we want to do are:
            • Set the security config to `system armed` : system_armed = True
            • Flash the status LED and leave it on afterwards, as an indication that the system is armed
            • Start up the `system armed` thread, which essentially checks for loud sound signals from the sound sensor
                and checks for motion detection from the cameras
            • As an extra (if capable), we may try to lock the doors of the vehicle by sending some form of signals
                from the raspberry pi

        returns:
            bool
        """
        self.security_config.system_armed = True
        if not self.no_hardware:
            self.hwcontroller.status_led_flash(SecurityServer._FLASH_SYSTEM_ARMED)
            self.hwcontroller.status_led_on()
        system_armed_thread = Thread(target=self._system_armed_thread)
        system_armed_thread.start()

        return self.security_config.system_armed

    def _disarm_system(self):
        """disarms the security system

        In this process, the things we want to do are:
            • Set the security config to `system disarmed` : system_armed = False
            • Flash the status LED and leave it off afterwards, as an indication that the system has been disarmed
            • As an extra (if capable), we may try to unlock the doors of the vehicle by sending some form of signals
                from the raspberry pi

        returns:
            bool
        """
        self.security_config.system_armed = False
        if self.security_config.cameras_live:
            self.security_config.cameras_live = False
        if not self.no_hardware:
            self.hwcontroller.status_led_flash(SecurityServer._FLASH_SYSTEM_DISARMED)

        return not self.security_config.system_armed

    def _system_armed_thread(self):
        """starts once the system has been armed

        Before starting this thread, we can safely assume that the `system_armed` config attribute has been set to
        True. That means, in this method, we can loop until that value has been set to false. It will only be set to
        false if a client sends data to the server to do so (Hence, disarming the system).

        In this process, the things we want to do are:
            • Read from the camera, getting the status and motion detected values from it.
            • If we have successfully read from the camera and motion has been detected, someone has either broken
                into the car, or its a false alarm (Kids are playing on the back seat) :)
            • To be on the safe side, we assume its a break in, and fire up the `system_breached_thread`
            • If motion hasnt been detected, we just continue to check until the system is disarmed
        """
        _logger.debug('System armed. - {:%Y-%m-%d %-I:%M %p}.avi'.format(datetime.datetime().now()))
        while self.security_config.system_armed:
            if not self.no_hardware:
                status1, _, motion_detected1 = self.videostream1.get_frame()
                status2, _, motion_detected2 = self.videostream2.get_frame()
                if status1 or status2:
                    if motion_detected1 or motion_detected2:
                        self.security_config.system_breached = True
                        self.hwcontroller.status_led_flash_start()
                        self.sock.send_data(SecurityServer._SYSTEM_BREACHED)
                        system_breach_thread = Thread(target=self._system_breached_thread, args=())
            time.sleep(0.2)

    def _system_breached_thread(self):
        """starts once the system has been breached

        This method is fired as a separate thread once the system is armed and motion or loud sound has been detected.

        In this process, we want to:
            • Initialize video writer object to record video to, and save the files on the server.
                - Video files are saved with the following format: system-breach-stream1-{:%Y-%m-%d %-I:%M %p}.avi
                - Using this format, we can easily operate on filenames to access files from particular dates and
                    times as we please.
            • While the `system_breached` security setting is set to True, update the video files with more frames.
            • While this is happeneing, the `security_thread` will still be up, and the client can easily look at
                the live stream while we are recording video.
            • The thread will stop once we either recieve false alarm data from the client, or they reach out to dispatchers
                and the situation is resolved.
        """
        _logger.debug('System breached. - {:%Y-%m-%d %-I:%M %p}.avi'.format(datetime.datetime().now()))
        # video recorder
        fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
        video_writer1 = cv2.VideoWriter("system-breach-stream1-{:%Y-%m-%d %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        video_writer2 = cv2.VideoWriter("system-breach-stream2-{:%Y-%m-%d %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        while self.security_config.system_breached:
            if not self.no_hardware:
                status1, frame1 = self.videostream1.read()
                status2, frame2 = self.videostream2.read()
                if status1:
                    video_writer1.write(frame1)
                if status2:
                    video_writer2.write(frame2)

    def _videostream_thread(self, stream):
        """starts when we recieve data to start live stream

        This process is fairly simple:
            • At the start of the `security_server_thread`, we start the video stream(s).
            • We simply read frames from the camera, and send the data to the client
            • This will be a really fast process, essentially of the server sending a bunch of pictures, but appear
                as a live video stream.
            • This process happens until the client stops it (hence, changes the security config `cameras_live` to false)
        """
        _logger.debug('Video started. - {:%Y-%m-%d %-I:%M %p}.avi'.format(datetime.datetime().now()))
        """thread for streaming video data to socket"""
        while self.security_config.cameras_live:
            if not self.no_hardware:
                status, data, _ = stream.get_frame()
                if status:
                    self.sock.send_data(data)
                else:
                    self.sock.send_data(SecurityServer._FAILURE)
            time.sleep(0.2)

    def _save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""
        self.sock.close()
        self.security_config.store_config()
        self.device_manager.store_devices()
        if not self.no_hardware:
            if self.videostream1.stream_running:
                self.videostream1.stop_stream()
            if self.videostream2.stream_running:
                self.videostream2.stop_stream()

    def _security_thread(self, addr, first_conn=False):
        """main security thread

        Essentially, in this method, we want to:
            • Recieve data from client
            • Make some type of action based on the data recieved
            • Send data to client

        This constantly happens until the socket is broken or the client disconnects from the server.

        args:
            addr: str
            first_conn: bool
        """
        _logger.debug('Security thread started. - {:%Y-%m-%d %-I:%M %p}.avi'.format(datetime.datetime().now()))

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

            elif data == SecurityServer._FALSE_ALARM:
                # System breach false alarm
                if self.security_config.system_breached:
                    self.security_config.system_breached = False
                    self.sock.send_data(SecurityServer._SUCCESS)
            elif data == SecurityServer._DISCONNECT:
                # Disconnect client
                device = self.device_manager.find_device(addr)
                _logger.debug('Device addr[{0}] name[{1}] disconnecting.'.format(device.address, device.name))
                break

        self._save_settings()
