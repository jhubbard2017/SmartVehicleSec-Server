# -*- coding: utf-8 -*-
#
# Test for securityserverpy.config.Config
#

import os
import unittest
import yaml

from securityserverpy.config import Config


class TestConfig(unittest.TestCase):
    """set of tests for config.Config"""

    def setUp(self):
        self.config = Config(config_file_name='tests/data/testconfig.yaml')

    def tearDown(self):
        self.config.reset_config()
        self.config.store_config()

    def test_example_yaml(self):
        self.assertIsNotNone(self.config)
        self.assertEqual(self.config.system_armed, False)

    def test_access_attributes(self):
        self.assertFalse(self.config.system_armed)
        self.assertFalse(self.config.cameras_live)
        self.assertFalse(self.config.system_breached)

    def test_set_attributes(self):
        self.config.system_armed = True
        self.config.cameras_live = True
        self.config.system_breached = True
        self.assertTrue(self.config.system_armed)
        self.assertTrue(self.config.cameras_live)
        self.assertTrue(self.config.system_breached)

    def test_store_config(self):
        self.config.system_armed = True
        self.config.cameras_live = True
        self.config.system_breached = True
        self.config.store_config()

        newconfig = Config(config_file_name='tests/data/testconfig.yaml')
        self.assertEqual(self.config.system_armed, newconfig.system_armed)
        self.assertEqual(self.config.cameras_live, newconfig.cameras_live)
        self.assertEqual(self.config.system_breached, newconfig.system_breached)