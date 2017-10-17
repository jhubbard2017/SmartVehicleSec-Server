# Smart Vehicle Security Server
Python server software for the Smart Vehicle Security System.

## Usage Examples
### Running on local machine
- this example assumes a python virtual env has already been established - see details on virtual env
```shell
(venv-securityserverpy) $ securityserverpy 
```
- the required arguments are the ip address and port number. These two need to be specified to start the program.
- When in development mode, use the `-d` argument so the database tables can be cleared after stopping the server.

### Tips for development mode
- When running and making api calls, use the `curl` command to send http request, as an example below.
Each api route uses a post method so that json data can be accessed via server.
```shell
$ curl -H "Content-Type: application/json" -X POST -d '{"key": "value", }' http://{ip_address}:{port}/path/to/route
```
- Make sure if testing with security client, server is booted up first so that the client can initialize its system by updating the server with the current connection parameters.

# Postgres Database
The server uses a postgreSQL 9.6 database.

## Setup and startup
- Use the following command to install postgres using brew (make sure brew is installed and updated to latest version):
```shell
$ brew install postgresql
```
- To start up the postgres server (You have to do this before running the security server):
```shell
$ make postgres
```
- To create the database and setup as user, run the following commands:
```shell
$ psql -d postgres -h localhost
$ CREATE DATABASE "smartVSecDatabase";
$ CREATE ROLE "smartVSecUser" LOGIN PASSWORD 'smartVSecDatabase';
$ CREATE SCHEMA secmonkey
$ GRANT Usage, Create ON SCHEMA "smartVSecDatabase" TO "smartVSecUser";
```
- Exit the postgres CLI tool:
```shell
$ CTRL-D
```
- Now, access the database to make sure it was successfully created:
```shell
$ psql -d smartVSecDatabase -h localhost
```
- Once you have successfully set up the database, you can use the `create_tables.py` file to set up the tables in the database.
This assumes you are in the virtual environment `venv-securityserverpy`. See details above.
```shell
(venv-securityserverpy) $ python securityserverpy/database/create_tables.py
```

# FLASK
The server uses a REST API for system access via a client mobile app or raspberry pi client.
Each path includes a leading string of `http://{localhost}:3001/path/to/route`

## Routes
Below is a list of routes available via API calls on the server. 
See code for details concerning required data for each route.

#### Authentication
- Root path: `/authentication`

  - `/login`: used to log in a user
  - `/logout`: log out a user
  - `/forgot_password`: sends email with new password

#### Users
- Root path: `/users`

  - `/add`: adds a user
  - `/get`: gets a user
  - `/remove`: removes a user
  - `/update`: updates a user
  - `/change_password`: updates a user password

#### Emergency Contacts
- Root path: `/emergency_contacts`

  - `/add`: adds list of contacts for user
  - `/get`: gets list of contacts for user
  - `/update`: updates contacts for user

#### Security
- Root path: `/security`

  - `/get_config`: get security config for system
  - `/add_config`: add security config for system
  - `/arm`: arm system
  - `/disarm`: disarm system
  - `/false_alarm`: set system breach as false alarm
  - `/panic`: send panic email to emergency contacts
  - `/set_breach`: set system as breach
  - `/get_logs`: get logs for system

#### Connections
- Root path: `/connections`

  - `/add`: add connection for system
  - `/get`: get connection for system
  - `/update`: update connection for system

#### Systems
- Root path: `/systems`

  - `/temperature`: get temperature data for system
  - `/speedometer`: get speedometer data for system
  - `/location`: get location data for system

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
- Only use this when we test the entire system

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
- pre-commit is currently not being used by this program.

## running your code
Writing code is great. But running it is usually the end goal. In `setup.py` the `entry_points` section defines command-line entry points for running your code. Inside your virtualenv, run:
```shell
$ securityserverpy
```
- See the above section on required arguments to successfully run the program.

## Versioning your code
There is a single definition of the package version in `securityserver/version.py`. Updating there changes the package version.

# Testing

## running automated tests
- Test are organized using the `unittest` framework provided by python. To setup tests and successfully close them, use the `setUp` and `tearDown` methods
- Examples are in the current test files in the project.
```shell
$ make test
```

## running automated tests with a debugger
- If you need to run test with a debugger, then use the following command:
```shell
$ make testpdb
```

## Contributing
- If you want to contribute, create a new branch and update your code. The master branch is protected, so submit a pull request and let another contributor review it.
- Before submitting PR, please make sure the program successfully runs as expected and that all tests are passing and not polluting.