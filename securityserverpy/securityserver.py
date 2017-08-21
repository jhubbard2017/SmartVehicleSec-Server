# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

from threading import Thread
import time
import datetime
from flask import Flask, jsonify, request, abort
import requests

from securityserverpy import _logger
from securityserverpy.devices import DeviceManager
from securityserverpy.hwcontroller import HardwareController
from securityserverpy.config import Config
from securityserverpy.logs import Logs
from securityserverpy.videostreamer import VideoStreamer


_SUCCESS_CODE = 201
_FAILURE_CODE = 404

app = Flask(__name__)

class SecurityServer(object):
    """handles server-client communication and processing of data sent and recieved

    SecurityServer module uses Flask to allow the server to operate as a REST API server

    Using this approach, we don't have to manager connections to clients and we can literally "rest"
    when the client doesn't need to send a command or retrieve data. Only when the client needs it do we actually
    do the work.
    """

    # Constants
    _DEFAULT_CAMERA_ID = 0
    _GEOIP_HOSTNAME = "http://freegeoip.net/json"

    # status LED flash signals
    _FLASH_NEW_DEVICE = 3
    _FLASH_SYSTEM_ARMED = 10
    _FLASH_SYSTEM_DISARMED = 5
    _FLASH_DEVICE_CONNECTED = 4
    _FLASH_SERVER_ON = 3

    # Log constants
    _USER_CONTROLLED_LOG_TYPE = 'user_controlled_type'
    _SECURITY_CONTROLLED_LOG_TYPE = 'security_controlled_type'

    def __init__(self, host, http_port, no_hardware=False, no_video=False, testing=False):
        """constructor method for SecurityServer

        HardwareController: used to control all pieces of hardware connected to the raspberry pi
        DeviceManager: module used to store device information that connects to the server
        SecurityConfig: a collection of security attributes about the system (system armed, cameras live, etc.)
        VideoStreamer: module to control video streaming to clients from server, and motion detection

        We use the 2 config values (no_hardware and no_video) for different development modes
        """
        self.host = host
        self.http_port = http_port
        self.device_manager = DeviceManager()
        self.security_config = Config()
        self.logs = Logs()

        self.no_hardware = no_hardware
        self.no_video = no_video

        # Set up different configs if needed
        if not self.no_hardware:
            self.hwcontroller = HardwareController()
        if not self.no_video:
            self.videostream = VideoStreamer(SecurityServer._DEFAULT_CAMERA_ID, self.no_video)
        if testing:
            self.device_manager = DeviceManager(file_name='tests/data/testdevices.yaml')
            self.security_config = Config(config_file_name='tests/data/testconfig.yaml')
            self.logs = Logs(file_name='tests/data/testlogs.yaml')

        # To make the REST API (Flask) methods work, we use inner methods
        # Also, all api request from the user requires a device name, which is hashed in the system.
        # In order to recieve a successful request code and expected data, the device name hash must exist in our system

        # Error handling
        @app.errorhandler(_FAILURE_CODE)
        def not_found(error):
            return jsonify({'code': _FAILURE_CODE,'data': 0})

        # Request config
        @app.route('/system/config/all', methods=['POST'])
        def get_config():
            """returns the security config"""
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)
            _logger.debug("Successful! Sending all security config to client.")
            return jsonify({'code': _SUCCESS_CODE, 'data': self.security_config.config})

        # Request 'system armed' status from config
        @app.route('/system/config/system_armed', methods=['POST'])
        def get_system_armed():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)

            _logger.debug("Successful! Sending security config (system_armed) to client.")
            return jsonify({'code': _SUCCESS_CODE, 'data': self.security_config.system_armed})

        # Request 'cameras live' status from config
        @app.route('/system/config/cameras_live', methods=['POST'])
        def get_cameras_live():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)

            _logger.debug("Successful! Sending security config (cameras_live) to client.")
            return jsonify({'code': _SUCCESS_CODE, 'data': self.security_config.cameras_live})

        # Request 'system breached' status from config
        @app.route('/system/config/system_breached', methods=['POST'])
        def get_system_breached():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)

            _logger.debug("Successful! Sending security config (system_breached) to client.")
            return jsonify({'code': _SUCCESS_CODE, 'data': self.security_config.system_breached})

        # Request add new device to system
        @app.route('/system/devices', methods=['POST'])
        def add_new_device():
            """adds new device

            Todo: check if this actually works
            """
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                success = self.device_manager.add_device(name)
                if success:
                    self.logs.add_log("Device added - {0}".format(name), SecurityServer._USER_CONTROLLED_LOG_TYPE)
                    if not self.no_hardware:
                        self.hwcontroller.status_led_flash(SecurityServer._FLASH_NEW_DEVICE)
                else:
                    _logger.debug("Error. Failure adding device.")
                    abort(_FAILURE_CODE)
            _logger.debug("Successful! Added new device to system.")
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        # Request to arm/disarm system
        @app.route('/system/arm', methods=['POST'])
        def arm_system():
            """Arms or disarms the system, depending on whether the request is true or false"""
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)
            if request.json['data'] == True:
                # Arm system
                if not self.security_config.system_armed:
                    self.security_config.system_armed = True
                    self.logs.add_log("System armed", SecurityServer._USER_CONTROLLED_LOG_TYPE)
                else:
                    abort(_FAILURE_CODE)

                if not self.no_hardware:
                    # Flash led then leave it on
                    self.hwcontroller.status_led_flash(SecurityServer._FLASH_SYSTEM_ARMED)
                    self.hwcontroller.status_led_on()

                system_armed_thread = Thread(target=self._system_armed_thread)
                system_armed_thread.start()
            elif request.json['data'] == False:
                # Disarm system
                if self.security_config.system_armed:
                    self.security_config.system_armed = False
                    self.logs.add_log("System disarmed", SecurityServer._USER_CONTROLLED_LOG_TYPE)
                else:
                    _logger.debug("Error. System already armed.")
                    abort(_FAILURE_CODE)

                if self.security_config.cameras_live:
                    self.security_config.cameras_live = False
                if not self.no_hardware:
                    self.hwcontroller.status_led_flash(SecurityServer._FLASH_SYSTEM_DISARMED)

            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        # Request to get list of system logs
        @app.route('/system/logs', methods=['GET'])
        def get_logs():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)
            all_logs = self.logs.get_logs()
            return jsonify({'code': _SUCCESS_CODE, 'data': all_logs})

        # Request to set breach as false alarm
        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)
            if self.security_config.system_breached:
                self.security_config.system_breached = False
            return jsonify({'code': _SUCCESS_CODE, 'data': self.security_config.system_breached})

        # Request to get current GPS location of system
        @app.route('/system/location', methods=["POST"])
        def get_location_coordinates():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)

            position = self._fetch_location_coordinates()
            return jsonify({'code': _SUCCESS_CODE, 'data': position})

        # Request to get current temperature
        @app.route('/system/temperature', methods=["POST"])
        def get_temperature():
            if not request.json or not 'name' in request.json:
                _logger.debug("Error! Name not found in request data.")
                abort(_FAILURE_CODE)
            else:
                name = request.json['name']
                if not self.device_manager.device_exist(name):
                    _logger.debug("Error. Device does not exist.")
                    abort(_FAILURE_CODE)

            ctemp, ftemp = self.hwcontroller.read_thermal_sensor()
            data = {'ctemp': ctemp, 'ftemp': ftemp}
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

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
        _logger.debug('System armed in 5 secs.')
        time.sleep(5)
        while self.security_config.system_armed:
            if not self.no_hardware and not self.no_video:
                motion_detected = self.hwcontroller.read_motion_sensor()
                noise_detected = self.hwcontroller.read_noise_sensor()
                if motion_detected or noise_detected:
                    self.security_config.system_breached = True
                    self.hwcontroller.status_led_flash_start()
                    system_breach_thread = Thread(target=self._system_breached_thread)
                    system_breach_thread.start()
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
        _logger.debug('System breached.')
        self.logs.add_log("System breached", SecurityServer._SECURITY_CONTROLLED_LOG_TYPE)
        # video recorder
        fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
        video_writer = cv2.VideoWriter("system-breach-recording-{:%b %d, %Y %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        while self.security_config.system_breached:
            if not self.no_hardware:
                status, frame_jpeg, frame = self.videostream.read()
                if status:
                    video_writer.write(frame)

    def save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""
        _logger.debug('Saving security session.')

        # Clear device list and reset security config for testing
        # Todo: change during production
        self.security_config.reset_config()
        self.device_manager.clear()
        self.logs.clear()

        self.security_config.store_config()
        self.device_manager.store_devices()
        self.logs.store_logs()
        if not self.no_hardware:
            self.videostream.release_stream()

    def start(self):
        """starts the flask app"""
        app.run(host=self.host, port=self.http_port)

    def server_app(self):
        return app

    def _fetch_location_coordinates(self):
        """fetches the location coordinates of the system, using the freegeoip/ host

        returns:
            dict -> {'latitude': float, 'longitude': float}
        """
        geo = requests.get(self._GEOIP_HOSTNAME)
        json_data = geo.json()
        position = {
            "latitude": float(json_data["latitude"]),
            "longitude": float(json_data["longitude"])
        }
        return position
