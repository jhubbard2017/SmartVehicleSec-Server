# -*- coding: utf-8 -*-
#
# utility class for exposing config read from/store in yaml file
#

import os
import yaml

from securityserverpy import _logger

class Config(object):
    """a utility class to read/store config and present it as properties

    reads in order from a local config yaml file, full of config and present values as properties
    the default name of the config file is `securityconfig.yaml`

    Once the connection to a client is loss, the updated config values need to be stored in the
    `securityconfig.yaml` file, so they can be read as the current state of the server
    """

    _DEFAULT_YAML_FILE_NAME = 'securityconfig.yaml'

    def __init__(self, config_file_name=None):
        """retrieve config from the yaml file

        error handling for two specific cases:
        - failing to open/read config file
        - failing to parse config file

        Config is automatically loaded once server is started

        args:
            config_file_name: filename str
        """
        self.values = {}
        self.local_file_name = config_file_name or Config._DEFAULT_YAML_FILE_NAME
        self._load_config()


    def _load_config(self):
        """loads security configuration data from local config file"""
        try:
            with open(self.local_file_name, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            return

        for key, value in file_contents.iteritems():
            if key not in self.values:
                self.values[key] = value
                _logger.debug('Adding key[{0}] from security config'.format(key))
            else:
                _logger.debug('Ignoring key [{0}] from security config'.format(key))

    def store_config(self):
        """stores the current config state in `securityconfig.yaml` file

        returns:
            bool
        """
        success = True
        try:
            with open(self.local_file_name, 'w') as fp:
                yaml.dump(self.values, fp)
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not write to file [{0}]'.format(exception))
            return not success

        return success

    @property
    def system_armed(self):
        return self.values.get('system_armed')

    @system_armed.setter
    def system_armed(self, value):
        self.values['system_armed'] = value

    @property
    def system_disarmed(self):
        return self.values.get('system_disarmed')

    @system_disarmed.setter
    def system_disarmed(self, value):
        self.values['system_disarmed'] = value

    @property
    def cameras_live(self):
        return self.values.get('cameras_live')

    @cameras_live.setter
    def cameras_live(self, value):
        self.values['cameras_live'] = value
