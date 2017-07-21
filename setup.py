# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

from securityserver.version import __version__

setup(
    name='Vechicle Security System Server',
    version=__version__,
    author='Jordan Hubbard',
    author_email='jhubb95@yahoo.com',
    description='a python server for the Smart Vehicle Security System',
    packages=find_packages(),
    setup_requires='setuptools',
    install_requires=[
        'RPi',
        'xmltodict',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'securityserver=securityserver.main:main',
        ]
    }
)