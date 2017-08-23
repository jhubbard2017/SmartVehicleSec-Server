# -*- coding: utf-8 -*-
#
# device client manager
#

import os
import yaml
import hashlib

from securityserverpy import _logger


class DeviceManager(object):
    """manages clients connected to socket"""

    _DEFAULT_DEVICES_FILE = 'yamls/devices.yaml'
    _DEVICE_LIMIT = 5

    def __init__(self, file_name=None):
        self.devices = []
        self.local_file_name = file_name or DeviceManager._DEFAULT_DEVICES_FILE
        self._load_devices()

    def _load_devices(self):
        """loads security configuration data from local config file"""
        try:
            with open(self.local_file_name, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            self.devices_loaded = False
            return

        self.devices = file_contents['devices']

    def clear(self):
        """removes all members of device manager"""
        self.devices = []

    def store_devices(self):
        """stores the current devices in yaml file

        returns:
            bool
        """
        success = True
        to_store = {'devices': self.devices}

        if not os.path.exists(self.local_file_name):
            _logger.debug('Could not write to file [{0}]'.format(self.local_file_name))
            return not success

        with open(self.local_file_name, 'w') as fp:
            yaml.dump(to_store, fp)

        return success

    def device_exist(self, name):
        """check if device already exists

        args:
            addr: str

        returns:
            bool
        """
        name_hash = self.name_hash(name)
        return name_hash in self.devices

    def add_device(self, name):
        """store new device in device manager

        args:
            addr: str
        """
        success = True
        if len(self.devices) < DeviceManager._DEVICE_LIMIT:
            name_hash = self.name_hash(name)
            if name_hash not in self.devices:
                self.devices.append(name_hash)
                return success
        return not success

    def remove_device(self, name):
        """removes a device from device manager

        args:
            addr: str
        """
        success = True
        name_hash = self.name_hash(name)
        if name_hash in self.devices:
            self.devices.remove(name_hash)
            return success
        return not success

    def device_count(self):
        """gets the number of devices in Device manager

        returns:
            int
        """
        return len(self.devices)

    def name_hash(self, name):
        m = hashlib.sha1()
        m.update(name.lower())
        return m.hexdigest()
