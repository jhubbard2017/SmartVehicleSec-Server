# -*- coding: utf-8 -*-
#
# testing for devices module
#

import unittest

from securityserverpy.devices import DeviceManager


class TestDeviceManager(unittest.TestCase):
    """set of test for devices.DeviceManager"""

    def setUp(self):
        self.name1 = 'device 1'
        self.name2 = 'device2'
        self.manager = DeviceManager(file_name='tests/data/testdevices.yaml')
        self.manager.clear()

    def tearDown(self):
        self.manager.clear()
        self.manager.store_devices()

    def test_devices_file_error(self):
        manager = DeviceManager(file_name='file doesnt exist')
        self.assertFalse(manager.devices_loaded)

        success = manager.store_devices()
        self.assertFalse(success)

    def test_add_devices(self):
        """test add devices to device manager"""
        self.manager.add_device(self.name1)
        self.manager.add_device(self.name2)

        self.assertEqual(self.manager.device_count(), 2)
        self.assertTrue(self.manager.device_exist(self.name1))
        self.assertTrue(self.manager.device_exist(self.name2))

    def test_add_device_over_limit(self):
        for x in range(5):
            self.manager.add_device('name{0}'.format(x))
        success = self.manager.add_device('foo')
        self.assertFalse(success)

    def test_remove_device(self):
        """test remove device from device manager"""
        self.manager.add_device(self.name1)
        self.manager.add_device(self.name2)

        self.assertEqual(self.manager.device_count(), 2)
        self.manager.remove_device(self.name1)
        self.assertFalse(self.manager.device_exist(self.name1))
        self.assertEqual(self.manager.device_count(), 1)

    def test_remove_device_not_exist(self):
        self.manager.add_device(self.name1)
        success = self.manager.remove_device(self.name2)
        self.assertFalse(success)

    def test_device_exist(self):
        """test get device"""
        self.manager.add_device(self.name1)
        self.manager.add_device(self.name2)
        self.assertTrue(self.manager.device_exist(self.name1))
        self.assertTrue(self.manager.device_exist(self.name2))

    def test_device_not_exist(self):
        """test get device fails"""
        self.assertFalse(self.manager.device_exist(self.name1))
        self.assertFalse(self.manager.device_exist(self.name2))

    def test_store_devices(self):
        """test store devices in yaml file"""
        manager = DeviceManager(file_name='tests/data/testdevices.yaml')
        manager.add_device(self.name1)
        manager.store_devices()

        new_manager = DeviceManager(file_name='tests/data/testdevices.yaml')

        self.assertEqual(manager.device_count(), new_manager.device_count())
        self.assertTrue(manager.device_exist(self.name1))
        self.assertTrue(new_manager.device_exist(self.name1))
