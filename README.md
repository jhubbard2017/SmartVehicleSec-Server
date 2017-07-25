# Smart Vehicle Security Server
Python server software for the Smart Vehicle Security System.

## Usage Examples
### running on local machine
- this example assumes a python virtual env has already been established - see details on virtual env
- this example does not trigger any calls to hardware devices
```shell
(venv-securityserverpy) $ securityserverpy -g
```

### running with specified port
```shell
(venv-securityserverpy) $ securityserverpy -p 8000
```

### running on raspberry pi
- this example assumes a python virtual env has already been established - see details on virtual env
```shell
(venv-securityserverpy) $ securityserverpy
```

# Config

## Config File
`securityserverpy` uses a yaml config file. to create a config:
```shell
cp serverconfig.yaml.example serverconfig.yaml
```
then fill out the missing values in the config file.

## Config Values
- `system_armed` security system is armed
- `system_breached` security system has been breached
- `cameras_live` cameras are currently live and/or recording

## Devices File
`securityserverpy` uses a yaml devices file. to create a device file:
```shell
cp devices.yaml.example devices.yaml
```

## Devices Values
For flexibility purposes, users may be able to connect more than one device/client to our security server.
- `devices` list of connected and allowed devices

# Python Details
## first time python setup
before beginning few prerequisite python packages must be installed and up to date. on macos:
```shell
$ sudo easy_install --upgrade pip virtualenv tox
```

## virtualenv
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) is a fantastic tools for creating python environments.

To easily create a virtualenv for development:
```shell
$ make develop
```

To easily create a virtualenv for production:
```shell
$ make prod
```

To begin using the virtual:
```shell
$ source venv-securityserverpy/bin/activate
```

The packages installed into the virtualenv are dictated by two files
### `requirements.txt`
In this file, all packages required to run the tool should be listed. Specify the exact version of the packages so that changes in dependencies don't break your tool.
### `requirements-dev.txt`
In this file, additional packages required to test the tool should be listed. Generally, the exact version is not specified.

## pre-commit
[pre-commit](http://pre-commit.com) is a tool to find and fix common issues before changes are committed. `pre-commit` will run before each `git commit`.
To run `pre-commit` on demand:
```shell
$ pre-commit run -a
```

## running your code
Writing code is great. But running it is usually the end goal. In `setup.py` the `entry_points` section defines command-line entry points for running your code. Inside your virtualenv, run:
```shell
$ securityserverpy
```

## Versioning your code
There is a single definition of the package version in `securityserver/version.py`. Updating there changes the package version.

# Testing
## running automated tests
```shell
$ make test
```

## running automated tests with a debugger
```shell
$ make testpdb
```