# Smart Vehicle Security Server
Python server software for the Smart Vehicle Security System.

## Usage Examples
### running on local machine
- this example assumes a python virtual env has already been established - see details on virtual env
- this example performs a dryrun which doesn't send data to connect clients
```shell
(venv-securityserver) $ securityserver --dryrun
```

### running on raspberry pi
- this example assumes a python virtual env has already been established - see details on virtual env
```shell
(venv-securityserver) $ securityserver
```

# Config

## Config File
securityserver uses a yaml config file. to create a config:
```shell
cp config.yaml.example config.yaml
```
then fill out the missing values in the config file.

## Config Values
- `dry_run` will not send data to connected client
- more config values wil be added as the project progresses

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
$ source venv-securityserver/bin/activate
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
$ securityserver
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