# -*- coding: utf-8 -*-
#
# main file: smart vehicle security server
#

import os
import xmltodict
from argparse import ArgumentParser

from securityserverpy import _logger
from securityserverpy.version import __version__
from securityserverpy.securityserver import SecurityServer

def _config_from_args():
    """sets up argparse to parse command line args

    returns:
        argparse.ArgumentParser
    """
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    optional_argument_group = parser.add_argument_group('optional arguments')
    optional_argument_group.add_argument(
        '-p', '--port', dest='port', default=None, required=False,
        help='Port number used for clients to access server. ')
    optional_argument_group.add_argument(
        '-g', '--no_hardware', dest='no_hardware', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')

    return parser.parse_args()


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
    _config_logging()
    config = _config_from_args()

    sec_server = SecurityServer(port=int(config.port), no_hardware=config.no_hardware)
    sec_server.start()


if __name__ == '__main__':
    main()
