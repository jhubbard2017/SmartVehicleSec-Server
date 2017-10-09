# -*- coding: utf-8 -*-
#
# mock for postgres database calls
#

from mock import Mock
import datetime

class DatabaseMock(object):

    def __init__(self):
        self.m_devices = {}
        self.r_devices = {}
        self.connections = {}
        self.securityconfig = {}
        self.logs = {}
        self.contacts = {}

        self.side_effect = False
        self.add_mobile_device_side_effect = False
        self.add_raspberry_pi_device_side_effect = False
        self.remove_mobile_device_side_effect = False
        self.remove_raspberry_pi_device_side_effect = False

    def add_side_effect(self):
        self.side_effect = True

    def remove_side_effect(self):
        self.side_effect = False

    def add_mobile_device(self, md_mac_address, name, email, phone, vehicle):
        if self.add_mobile_device_side_effect:
            return False
        self.m_devices[md_mac_address] = {'name': name, 'email': email, 'phone': phone, 'vehicle': vehicle}
        return md_mac_address in self.m_devices

    def remove_mobile_device(self, md_mac_address):
        if self.remove_mobile_device_side_effect:
            return False
        del self.m_devices[md_mac_address]
        return not md_mac_address in self.m_devices

    def update_mobile_device(self, md_mac_address, name=None, email=None, phone=None, vehicle=None):
        if not md_mac_address in self.m_devices:
            return False
        if name:
            self.m_devices[md_mac_address]['name'] = name
        if email:
            self.m_devices[md_mac_address]['email'] = email
        if phone:
            self.m_devices[md_mac_address]['phone'] = phone
        if vehicle:
            self.m_devices[md_mac_address]['vehicle'] = vehicle

        return True

    def get_mobile_device(self, md_mac_address):
        if not md_mac_address in self.m_devices:
            return None
        return md_mac_address

    def get_mobile_device_with_rd(self, rd_mac_address):
        for m_device, r_device in self.r_devices.iteritems():
            if r_device == rd_mac_address:
                return m_device
        return None

    def get_mobile_device_information(self, md_mac_address):
        if not md_mac_address in self.m_devices:
            return None
        return self.m_devices[md_mac_address]

    def add_raspberry_pi_device(self, md_mac_address, rd_mac_address):
        if self.add_raspberry_pi_device_side_effect:
            return False
        self.r_devices[md_mac_address] = rd_mac_address
        return md_mac_address in self.r_devices

    def remove_raspberry_pi_device(self, rd_mac_address):
        if self.remove_raspberry_pi_device_side_effect:
            return False
        for m_device, r_device in self.r_devices.iteritems():
            if r_device and r_device == rd_mac_address:
                del self.r_devices[m_device]
                break
        return True

    def get_raspberry_pi_device(self, md_mac_address):
        if not md_mac_address in self.r_devices:
            return None
        return self.r_devices[md_mac_address]

    def add_raspberry_pi_connection(self, rd_mac_address, ip_address, port):
        if rd_mac_address in self.connections:
            return False
        self.connections[rd_mac_address] = {'ip_address': ip_address, 'port': port}
        return True

    def update_raspberry_pi_connection(self, rd_mac_address, ip_address=None, port=None):
        if not rd_mac_address in self.connections:
            return False
        if ip_address:
            self.connections[rd_mac_address]['ip_address'] = ip_address
        if port:
            self.connections[rd_mac_address]['port'] = port
        return True

    def get_raspberry_pi_connection(self, rd_mac_address):
        if not rd_mac_address in self.connections:
            return None
        return self.connections[rd_mac_address]

    def remove_raspberry_pi_connection(self, rd_mac_address):
        if not rd_mac_address in self.connections:
            return False
        del self.connections[rd_mac_address]
        return True

    def add_contact(self, rd_mac_address, name, email, phone):
        if self.side_effect:
            self.side_effect = False
            return False
        if not rd_mac_address in self.contacts:
            self.contacts[rd_mac_address] = {name: {'email': email, 'phone': phone}}
        else:
            self.contacts[rd_mac_address].update({name: {'email': email, 'phone': phone}})
        return True

    def update_contact(self, rd_mac_address, name, email=None, phone=None):
        if not rd_mac_address in self.contacts:
            return False
        if not name in self.contacts[rd_mac_address]:
            return False
        if email:
            self.contacts[rd_mac_address][name]['email'] = email
        if phone:
            self.contacts[rd_mac_address][name]['phone'] = phone
        return True

    def remove_contact(self, rd_mac_address, name):
        if not rd_mac_address in self.contacts:
            return False
        if not name in self.contacts[rd_mac_address]:
            return False
        del self.contacts[rd_mac_address][name]
        return True

    def remove_all_contacts(self, rd_mac_address):
        if not rd_mac_address in self.contacts:
            return False
        del self.contacts[rd_mac_address]
        return True

    def get_contacts(self, rd_mac_address):
        if not rd_mac_address in self.contacts:
            return None
        contacts = []
        for name, contact in self.contacts[rd_mac_address].iteritems():
            contacts.append({'name': name, 'email': contact['email'], 'phone': contact['phone']})
        return contacts

    def add_log(self, rd_mac_address, info):
        current_date = datetime.datetime.now()
        date = '{:%b %d, %Y}'.format(current_date)
        time = '{:%-I:%M %p}'.format(current_date)
        log = {'date': date, 'time': time, 'info': info}
        if not rd_mac_address in self.logs:
            self.logs[rd_mac_address] = [log]
        else:
            self.logs[rd_mac_address].append(log)
        return True

    def get_logs(self, rd_mac_address):
        if not rd_mac_address in self.logs:
            return None
        return self.logs[rd_mac_address]

    def add_security_config(self, rd_mac_address):
        if rd_mac_address in self.securityconfig:
            return False
        self.securityconfig[rd_mac_address] = {'system_armed': False, 'system_breached': False}
        return True

    def update_security_config(self, rd_mac_address, system_armed=False, system_breached=False):
        if not rd_mac_address in self.securityconfig:
            return False
        if system_armed:
            self.securityconfig[rd_mac_address]['system_armed'] = system_armed
        if system_breached:
            self.securityconfig[rd_mac_address]['system_breached'] = system_breached
        return True

    def get_security_config(self, rd_mac_address):
        if not rd_mac_address in self.securityconfig:
            return None
        return self.securityconfig[rd_mac_address]

    def clear_all_tables(self):
        self.m_devices = {}
        self.r_devices = {}
        self.connections = {}
        self.securityconfig = {}
        self.logs = {}
        self.contacts = {}
        self.side_effect = False
