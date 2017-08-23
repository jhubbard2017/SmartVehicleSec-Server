import unittest

from securityserverpy.logs import Logs


class TestLogs(unittest.TestCase):
    """set of test for devices.DeviceManager"""

    _USER_CONTROLLED_TYPE = 'user_controlled_type'
    _SECURITY_CONTROLLED_TYPE = 'security_controlled_type'

    def setUp(self):
        self.logs = Logs(file_name='tests/data/testlogs.yaml')
        self.logs.clear()

    def tearDown(self):
        self.logs.clear()
        self.logs.store_logs()

    def test_logs_file_error(self):
        logs = Logs(file_name='file doesnt exist')
        self.assertFalse(logs.logs_loaded)

        success = logs.store_logs()
        self.assertFalse(success)

    def test_add_logs(self):
        self.logs.add_log('my info 1', TestLogs._USER_CONTROLLED_TYPE)
        self.logs.add_log('my info 2', TestLogs._SECURITY_CONTROLLED_TYPE)
        self.assertEqual(self.logs.log_count(), 2)

        my_logs = self.logs.get_logs()
        self.assertEqual(my_logs[TestLogs._USER_CONTROLLED_TYPE][0]['info'], 'my info 1')
        self.assertEqual(my_logs[TestLogs._SECURITY_CONTROLLED_TYPE][0]['info'], 'my info 2')

    def test_add_logs_user_log_limit(self):
        self.logs.add_log('log-1', TestLogs._USER_CONTROLLED_TYPE)
        for x in range(30):
            self.logs.add_log('log{0}'.format(x), TestLogs._USER_CONTROLLED_TYPE)

        all_user_logs = self.logs.get_logs()[TestLogs._USER_CONTROLLED_TYPE]
        for log in all_user_logs:
            self.assertNotEqual('log-1', log['info'])

    def test_add_logs_system_log_limit(self):
        self.logs.add_log('log-1', TestLogs._SECURITY_CONTROLLED_TYPE)
        for x in range(30):
            self.logs.add_log('log{0}'.format(x), TestLogs._SECURITY_CONTROLLED_TYPE)

        all_user_logs = self.logs.get_logs()[TestLogs._SECURITY_CONTROLLED_TYPE]
        for log in all_user_logs:
            self.assertNotEqual('log-1', log['info'])

    def test_store_logs(self):
        """test store devices in yaml file"""
        logs1 = Logs(file_name='tests/data/testlogs.yaml')
        logs1.add_log('log 1 info', TestLogs._USER_CONTROLLED_TYPE)
        logs1.add_log('log 2 info', TestLogs._SECURITY_CONTROLLED_TYPE)
        logs1.store_logs()

        logs2 = Logs(file_name='tests/data/testlogs.yaml')

        self.assertEqual(logs1.log_count(), logs2.log_count())
        self.assertEqual(logs1.get_logs(), logs2.get_logs())
