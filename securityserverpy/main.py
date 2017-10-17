# -*- coding: utf-8 -*-
#
# main module
#

import os
from argparse import ArgumentParser
from threading import Thread
import sys
import socket

from securityserverpy import _logger
from securityserverpy.version import __version__
from securityserverpy.server import Server


def _config_from_args():
    """sets up argparse to parse command line args

    returns:
        argparse.ArgumentParser
    """
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    optional_argument_group = parser.add_argument_group('optional arguments')
    optional_argument_group.add_argument(
        '-d', '--dev', dest='dev', action='store_true', default=False, required=False,
        help='Will clear databases after ending session.')

    return parser.parse_args()

# Make global so can be accessed when needed to stop system, and safely save settings
config = _config_from_args()
host = socket.gethostbyname(socket.gethostname())
port = 3001
server = Server(host=host, port=port, dev=config.dev)

def main_thread():
    """main thread to start up the server"""
    server.start()

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
            server.save_settings()
            sys.exit(0)

if __name__ == '__main__':
    main()
