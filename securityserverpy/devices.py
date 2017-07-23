# -*- coding: utf-8 -*-
#
# device client manager
#

import os
import yaml

from securityserverpy import _logger


class Device(object):
    """represents a single connected device"""

    def __init__(self, address, name=None):
        self._address = address
        self._name = name

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class DeviceManager(object):
    """manages clients connected to socket"""

    _DEFAULT_DEVICES_FILE = 'devices.yaml'
    _DEVICE_LIMIT = 3

    def __init__(self, file_name=None):
        self.devices = {}
        self.addrs_to_store = []
        self.local_file_name = file_name or DeviceManager._DEFAULT_DEVICES_FILE
        self.devices_loaded = True
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

        # First loop should only iterate once since `devices` is the only key in the file
        for key, value in file_contents.iteritems():
            if key == 'devices':
                for addr in value:
                    new_device = Device(addr)
                    self.devices[addr] = new_device
                    self.addrs_to_store.append(addr)

    def clear(self):
        """removes all members of device manager"""
        self.devices = {}
        self.addrs_to_store = []

    def store_devices(self):
        """stores the current devices in yaml file

        returns:
            bool
        """
        success = True
        to_store = {'devices': self.addrs_to_store}

        try:
            with open(self.local_file_name, 'w') as fp:
                yaml.dump(to_store, fp)
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not write to file [{0}]'.format(exception))
            return not success

        return success

    def device_exist(self, addr):
        """check if device already exists

        args:
            addr: str

        returns:
            bool
        """
        return addr in self.addrs_to_store

    def add_device(self, addr, name):
        """store new device in device manager

        args:
            addr: str
        """
        if len(self.devices) <= DeviceManager._DEVICE_LIMIT:
            new_device = Device(addr)
            new_device.name = name
            self.devices[addr] = new_device
            self.addrs_to_store.append(addr)

    def find_device(self, addr):
        """fetches a device in device manager

        args:
            addr: str

        returns:
                Device (if found)
                None (if not found)
        """
        status = addr in self.addrs_to_store
        if status:
            return self.devices.get(addr)

        return None

    def remove_device(self, addr):
        """removes a device from device manager

        args:
            addr: str
        """
        del self.devices[addr]
        self.addrs_to_store.remove(addr)

    def device_count(self):
        """gets the number of devices in Device manager

        returns:
            int
        """
        return len(self.devices)