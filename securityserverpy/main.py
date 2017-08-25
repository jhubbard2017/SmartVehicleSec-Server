# -*- coding: utf-8 -*-
#
# main file: smart vehicle security server
#

import os
from argparse import ArgumentParser
from threading import Thread
import sys

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
        '-i', '--host', dest='host', default=None, required=True,
        help='Port number used for clients to access server. ')
    optional_argument_group.add_argument(
        '-p', '--httpport', dest='http_port', default=None, required=True,
        help='Port number used for clients to access server. ')
    optional_argument_group.add_argument(
        '-nh', '--no_hardware', dest='no_hardware', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')
    optional_argument_group.add_argument(
        '-nv', '--no_video', dest='no_video', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')

    return parser.parse_args()

# Make global so can be accessed when need to stop system, and safely save settings
config = _config_from_args()
http_port = int(config.http_port)
sec_server = SecurityServer(host=config.host, http_port=http_port,
                            no_hardware=config.no_hardware, no_video=config.no_video)

def main_thread():
    """main thread to start up the server"""
    sec_server.start()

def main():
    """ main function

    set up configs and start server
        - Enter 'stop' to end the server and successfully save settings
    """
    thread = Thread(target=main_thread)
    thread.daemon = True
    thread.start()
    while True:
        text = raw_input()
        if text == "stop":
            _logger.info("Shutting down. Saving settings.")
            sec_server.save_settings()
            sys.exit(0)

if __name__ == '__main__':
    main()
