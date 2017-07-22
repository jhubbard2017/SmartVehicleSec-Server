# -*- coding: utf-8 -*-
#
# testing for devices module
#

import unittest

from securityserverpy.devices import Device
from securityserverpy.devices import DeviceManager


class TestDevice(unittest.TestCase):
    """set of test for devices.Device"""

    def setUp(self):
        self.addr = '123.4.5.678'
        self.name = 'My New Iphoe'

    def test_create_device(self):
        """test create new device"""
        new_device = Device(self.addr, name=self.name)
        self.assertEqual(new_device.address, self.addr)
        self.assertEqual(new_device.name, self.name)


class TestDeviceManager(unittest.TestCase):
    """set of test for devices.DeviceManager"""

    def setUp(self):
        self.addr1 = '123.4.5.678'
        self.addr2 = '987.6.5.432'
        self.manager = DeviceManager()

    def test_add_devices(self):
        """test add devices to device manager"""
        self.manager.add_device(self.addr1)
        self.manager.add_device(self.addr2)

        self.assertEqual(self.manager.device_count(), 2)
        self.assertTrue(self.manager.device_exist(self.addr1))
        self.assertTrue(self.manager.device_exist(self.addr2))

    def test_remove_device(self):
        """test remove device from device manager"""
        self.manager.add_device(self.addr1)
        self.manager.add_device(self.addr2)

        self.assertEqual(self.manager.device_count(), 2)
        self.manager.remove_device(self.addr1)
        self.assertFalse(self.manager.device_exist(self.addr1))
        self.assertEqual(self.manager.device_count(), 1)

    def test_get_device_success(self):
        """test get device"""
        self.manager.add_device(self.addr1)
        self.manager.add_device(self.addr2)

        device1 = self.manager.find_device(self.addr1)
        device2 = self.manager.find_device(self.addr2)

        self.assertEqual(device1.address, self.addr1)
        self.assertEqual(device2.address, self.addr2)

    def test_get_device_fails(self):
        """test get device fails"""
        device1 = self.manager.find_device(self.addr1)
        device2 = self.manager.find_device(self.addr2)

        self.assertTrue(device1 is None)
        self.assertTrue(device2 is None)
