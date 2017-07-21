# -*- coding: utf-8 -*-
#
# main file: smart vehicle security server
#

import os
import xmltodict

from securityserverpy import _logger
from securityserverpy.version import __version__
# more imports to come as project progresses


def _config_logging():
    """allow log level to be set by environment"""
    if 'SECURITYSERVER_LOG' in os.environ.keys():
        log_level = os.environ['SECURITYSERVER_LOG'].upper()
        _logger.setLevel(log_level)
        _logger.warn('set log level [{0}]'.format(log_level))


def main():
    """ main function

    set up configs, connect to client, and secure their vehicle :)
    """
    pass

if __name__ == '__main__':
    main()
