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
        self.address = address
        self.name = name

    @property
    def address(self):
        return self.address

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        self.name = value


class DeviceManager(object):
    """manages clients connected to socket"""

    _DEFAULT_DEVICES_FILE = 'devices.yaml'

    def __init__(self):
        self.devices = {}
        self.addrs_to_store = []
        self._load_config()

    def _load_config(self):
        """loads security configuration data from local config file"""
        try:
            with open(DeviceManager._DEFAULT_DEVICES_FILE, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            return

        # First loop should only iterate once since `devices` is the only key in the file
        for key, value in file_contents.iteritems():
            if key == 'devices':
                for addr in value:
                    new_device = Device(addr)
                    self.devices[addr] = new_device
                    self.addrs_to_store.append(addr)

    def device_exist(self, addr):
        """check if device already exists

        args:
            addr: str

        returns:
            bool
        """
        return addr in self.addrs_to_store

    def add_device(self, addr):
        """store new device in device manager

        args:
            addr: str
        """
        new_device = Device(addr)
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