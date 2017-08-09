# -*- coding: utf-8 -*-
#
# device client manager
#

import os
import yaml
import datetime

from securityserverpy import _logger


class Logs(object):
    """list of objects representing records of system actions

    Logs will be recorded data of the following actions:
        - User initiated (system armed, disarmed)
        - Security initiated (system breached)
    """

    _DEFAULT_LOGS_FILE = 'yamls/logs.yaml'
    _LOG_COUNT_LIMIT = 50

    _USER_CONTROLLED_TYPE = 'user_controlled_type'
    _SECURITY_CONTROLLED_TYPE = 'security_controlled_type'

    def __init__(self, file_name=None):
        self.user_controlled_logs = []
        self.security_controlled_logs = []
        self.local_file_name = file_name or DeviceManager._DEFAULT_DEVICES_FILE
        self._load_logs()

    def _load_logs(self):
        """loads log data from local yaml file"""
        try:
            with open(self.local_file_name, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            return

        for key, value in file_contents.iteritems():
            if key == 'user_controlled_logs':
                for x in value:
                    new_log = LogItem(x['title'], x['description'], x['timestamp'])
                    self.user_controlled_logs.append(new_log)
            if key == 'security_controlled_logs':
                for x in value:
                    new_log = LogItem(x['title'], x['description'], x['timestamp'])
                    self.security_controlled_logs.append(new_log)

    def clear(self):
        """removes all members of device manager"""
        self.user_controlled_logs = []
        self.security_controlled_logs = []

    def store_logs(self):
        """stores the current logs in yaml file

        returns:
            bool
        """
        success = True
        user_controlled_logs = []
        security_controlled_logs = []

        for log in self.user_controlled_logs:
            log_to_save = {'title': log.title, 'description': log.description, 'timestamp': log.timestamp}
            user_controlled_logs.append(log_to_save)
        for log in self.user_controlled_logs:
            log_to_save = {'title': log.title, 'description': log.description, 'timestamp': log.timestamp}
            security_controlled_logs.append(log_to_save)

        all_logs = {
            'user_controlled_logs': user_controlled_logs,
            'security_controlled_logs': security_controlled_logs
        }
        try:
            with open(self.local_file_name, 'w') as fp:
                yaml.dump(all_logs, fp)
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not write to file [{0}]'.format(exception))
            return not success

        return success

    def add_log(self, title, description, type):
        """adds new log to the system"""
        logs_full = len(self.user_controlled_logs) + len(self.security_controlled_logs) >= Logs._LOG_COUNT_LIMIT
        new_log = LogItem(title, description, ":%Y-%m-%d %-I:%M %p".format(datetime.datetime().now()))
        if type == Logs._USER_CONTROLLED_TYPE:
            if logs_full:
                del self.user_controlled_logs[0]
            self.user_controlled_logs.append(new_log)
        if type == Logs._SECURITY_CONTROLLED_TYPE:
            if logs_full:
                del self.security_controlled_logs[0]
            self.security_controlled_logs.append(new_log)

    def log_count(self):
        """gets total number of logs

        returns:
            int
        """
        return len(self.user_controlled_logs) + len(self.security_controlled_logs)


class LogItem(object):
    def __init__(self, title, description, timestamp):
        self.title = title
        self.description = description
        self.timestamp = timestamp