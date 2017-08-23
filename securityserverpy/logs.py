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
    _LOG_COUNT_LIMIT = 30

    _USER_CONTROLLED_TYPE = 'user_controlled_type'
    _SECURITY_CONTROLLED_TYPE = 'security_controlled_type'

    def __init__(self, file_name=None):
        self.user_controlled_logs = []
        self.security_controlled_logs = []
        self.local_file_name = file_name or Logs._DEFAULT_LOGS_FILE
        self._load_logs()

    def _load_logs(self):
        """loads log data from local yaml file"""
        try:
            with open(self.local_file_name, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            self.logs_loaded = False
            return

        self.user_controlled_logs = file_contents[Logs._USER_CONTROLLED_TYPE]
        self.security_controlled_logs = file_contents[Logs._SECURITY_CONTROLLED_TYPE]

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

        all_logs = {
            Logs._USER_CONTROLLED_TYPE: self.user_controlled_logs,
            Logs._SECURITY_CONTROLLED_TYPE: self.security_controlled_logs
        }

        if not os.path.exists(self.local_file_name):
            _logger.debug('Could not write to file [{0}]'.format(self.local_file_name))
            return not success

        with open(self.local_file_name, 'w') as fp:
            yaml.dump(all_logs, fp)

        return success

    def add_log(self, info, type):
        """adds new log to the system"""
        curr_date = datetime.datetime.now()
        new_log = new_log = {
            'info': info,
            'date': ":%b %d, %Y".format(curr_date),
            'time': "%-I:%M %p".format(curr_date)
        }
        if type == Logs._USER_CONTROLLED_TYPE:
            if len(self.user_controlled_logs) >= Logs._LOG_COUNT_LIMIT:
                del self.user_controlled_logs[0]
            self.user_controlled_logs.append(new_log)
        if type == Logs._SECURITY_CONTROLLED_TYPE:
            if len(self.security_controlled_logs) >= Logs._LOG_COUNT_LIMIT:
                del self.security_controlled_logs[0]
            self.security_controlled_logs.append(new_log)

    def get_logs(self):
        all_logs = {
            Logs._USER_CONTROLLED_TYPE: self.user_controlled_logs,
            Logs._SECURITY_CONTROLLED_TYPE: self.security_controlled_logs
        }
        return all_logs

    def log_count(self):
        """gets total number of logs

        returns:
            int
        """
        return len(self.user_controlled_logs) + len(self.security_controlled_logs)
