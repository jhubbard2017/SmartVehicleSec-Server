# -*- coding: utf-8 -*-
#
# mock for postgres database calls
#

from mock import Mock
import datetime

class DatabaseMock(object):

    def __init__(self):
        self.users = {}
        self.connections = {}
        self.securityconfig = {}
        self.logs = {}
        self.contacts = {}

    def add_user(self, email, password, firstname, lastname, phone, vehicle, system_id):
        self.users[email] = {
            'firstname': firstname, 'lastname': lastname, 'email': email, 'password': password,
            'phone': phone, 'vehicle': vehicle, 'system_id': system_id, 'logged_in': False
        }
        return True

    def remove_user(self, email):
        if not email in self.users:
            return False
        del self.users[email]
        return True

    def update_user(self, email, password=None, firstname=None, lastname=None, phone=None, vehicle=None, system_id=None, logged_in=None):
        if not email in self.users:
            return False
        if firstname:
            self.users[email]['firstname'] = firstname
        if lastname:
            self.users[email]['lastname'] = lastname
        if email:
            self.users[email]['email'] = email
        if phone:
            self.users[email]['phone'] = phone
        if vehicle:
            self.users[email]['vehicle'] = vehicle
        if password:
            self.users[email]['password'] = password
        if system_id:
            self.users[email]['system_id'] = system_id
        if logged_in != None:
            self.users[email]['logged_in'] = logged_in

        return True

    def get_user(self, email):
        if not email in self.users:
            return None
        return self.users[email]

    def verify_user(self, email, password):
        if not email in self.users:
            return None
        if not self.users[email]['password'] == password:
            return None
        return self.users[email]

    def get_user_with_system_id(self, system_id):
        for email, user in self.users.iteritems():
            if user['system_id'] == system_id:
                return user
        return None
    #
    # def add_raspberry_pi_connection(self, rd_mac_address, ip_address, port):
    #     if rd_mac_address in self.connections:
    #         return False
    #     self.connections[rd_mac_address] = {'ip_address': ip_address, 'port': port}
    #     return True
    #
    # def update_raspberry_pi_connection(self, rd_mac_address, ip_address=None, port=None):
    #     if not rd_mac_address in self.connections:
    #         return False
    #     if ip_address:
    #         self.connections[rd_mac_address]['ip_address'] = ip_address
    #     if port:
    #         self.connections[rd_mac_address]['port'] = port
    #     return True
    #
    # def get_raspberry_pi_connection(self, rd_mac_address):
    #     if not rd_mac_address in self.connections:
    #         return None
    #     return self.connections[rd_mac_address]
    #
    # def remove_raspberry_pi_connection(self, rd_mac_address):
    #     if not rd_mac_address in self.connections:
    #         return False
    #     del self.connections[rd_mac_address]
    #     return True
    #
    # def add_contact(self, rd_mac_address, name, email, phone):
    #     if self.side_effect:
    #         self.side_effect = False
    #         return False
    #     if not rd_mac_address in self.contacts:
    #         self.contacts[rd_mac_address] = {name: {'email': email, 'phone': phone}}
    #     else:
    #         self.contacts[rd_mac_address].update({name: {'email': email, 'phone': phone}})
    #     return True
    #
    # def update_contact(self, rd_mac_address, name, email=None, phone=None):
    #     if not rd_mac_address in self.contacts:
    #         return False
    #     if not name in self.contacts[rd_mac_address]:
    #         return False
    #     if email:
    #         self.contacts[rd_mac_address][name]['email'] = email
    #     if phone:
    #         self.contacts[rd_mac_address][name]['phone'] = phone
    #     return True
    #
    # def remove_contact(self, rd_mac_address, name):
    #     if not rd_mac_address in self.contacts:
    #         return False
    #     if not name in self.contacts[rd_mac_address]:
    #         return False
    #     del self.contacts[rd_mac_address][name]
    #     return True
    #
    # def remove_all_contacts(self, rd_mac_address):
    #     if not rd_mac_address in self.contacts:
    #         return False
    #     del self.contacts[rd_mac_address]
    #     return True
    #
    # def get_contacts(self, rd_mac_address):
    #     if not rd_mac_address in self.contacts:
    #         return None
    #     contacts = []
    #     for name, contact in self.contacts[rd_mac_address].iteritems():
    #         contacts.append({'name': name, 'email': contact['email'], 'phone': contact['phone']})
    #     return contacts
    #
    # def add_log(self, rd_mac_address, info):
    #     current_date = datetime.datetime.now()
    #     date = '{:%b %d, %Y}'.format(current_date)
    #     time = '{:%-I:%M %p}'.format(current_date)
    #     log = {'date': date, 'time': time, 'info': info}
    #     if not rd_mac_address in self.logs:
    #         self.logs[rd_mac_address] = [log]
    #     else:
    #         self.logs[rd_mac_address].append(log)
    #     return True
    #
    # def get_logs(self, rd_mac_address):
    #     if not rd_mac_address in self.logs:
    #         return None
    #     return self.logs[rd_mac_address]
    #
    # def add_security_config(self, rd_mac_address):
    #     if rd_mac_address in self.securityconfig:
    #         return False
    #     self.securityconfig[rd_mac_address] = {'system_armed': False, 'system_breached': False}
    #     return True
    #
    # def update_security_config(self, rd_mac_address, system_armed=False, system_breached=False):
    #     if not rd_mac_address in self.securityconfig:
    #         return False
    #     if system_armed:
    #         self.securityconfig[rd_mac_address]['system_armed'] = system_armed
    #     if system_breached:
    #         self.securityconfig[rd_mac_address]['system_breached'] = system_breached
    #     return True
    #
    # def get_security_config(self, rd_mac_address):
    #     if not rd_mac_address in self.securityconfig:
    #         return None
    #     return self.securityconfig[rd_mac_address]

    def clear_all_tables(self):
        self.users = {}
        self.connections = {}
        self.securityconfig = {}
        self.logs = {}
        self.contacts = {}
