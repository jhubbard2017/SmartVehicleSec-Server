# -*- coding: utf-8 -*-
#
# utility class managing panic response contacts and sending out alert emails
#

import os
import os.path
import yaml
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from securityserverpy import _logger


class PanicResponse(object):
    """handles panic response communication to selected contacts given by client

    With this module, we will be able to send text messages and emails to selected contacts
    when a bad alert is happening or when the panic button is pressed by someone in the vehicle
    """

    _DEFAULT_FILE = 'yamls/contacts.yaml'
    _CONTACTS_INDEX = 'contacts'
    _CONTACT_LIMIT = 15

    _MAIL_SERVER = 'smtp.gmail.com'
    _MAIL_PORT = 587
    _SYSTEM_EMAIL = 'smart.vehicle.sec@gmail.com'
    _SYSTEM_PASSWORD = 'seniordesign2017'
    _SYSTEM_EMAIL_SUBJECT = 'ALERT MESSAGE FROM [{0}]'

    def __init__(self, file_name=None):
        self.contacts = {}
        self.local_file_name = file_name or PanicResponse._DEFAULT_FILE
        self.total_emails_sent = 0
        self._load()

    def _load(self):
        """loads contact data from local yaml file"""
        try:
            with open(self.local_file_name, 'r') as fp:
                file_contents = yaml.load(fp.read())
        except (IOError, yaml.YAMLError) as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))
            self.contacts_loaded = False
            return

        self.contacts = file_contents[PanicResponse._CONTACTS_INDEX]

    def clear(self):
        """removes all contacts of PanicResponse"""
        self.contacts = {}

    def store(self):
        """stores the current contacts in yaml file

        returns:
            bool
        """
        success = True

        to_store = {
            PanicResponse._CONTACTS_INDEX: self.contacts
        }

        if not os.path.exists(self.local_file_name):
            _logger.debug('Could not write to file [{0}]'.format(self.local_file_name))
            return not success

        with open(self.local_file_name, 'w') as fp:
            yaml.dump(to_store, fp)

        return success

    def add_contact(self, name, phone, email):
        """creates new contact object and adds it to the list of contacts

        args:
            name: str
            phone: str
            email: str

        returns:
            bool
        """
        success = True
        if (len(self.contacts) >= PanicResponse._CONTACT_LIMIT) or self.contacts.get(name):
            return not success
        self.contacts[name] = {
            'phone': phone,
            'email': email
        }
        return success

    def remove_contact(self, name):
        """removes contact object (referenced from name) from contacts list

        args:
            name: str

        returns:
            bool
        """
        success = True
        if not self.contacts.get(name):
            return not success
        del self.contacts[name]
        return success

    def modify_contact(self, name, phone=None, email=None):
        """allows modification of phone or email for specific contact

        --->>> NAME CANNOT BE CHANGED AFTER BEING SET

        args:
            name: str
            phone: str
            email: str

        returns:
            bool
        """
        success = True
        if not self.contacts.get(name):
            return not success
        if phone:
            self.contacts[name]['phone'] = phone
        if email:
            self.contacts[name]['email'] = email
        return success

    def get_contact(self, name):
        """gets contact if exists

        args:
            name: str

        returns:
            dict || None
        """
        if self.contacts.get(name):
            return self.contacts[name]
        return None

    def contact_count(self):
        """gets number of total contacts"""
        return len(self.contacts)

    def send_message_all(self):
        """sends warning message (email) to all contacts"""
        for name, contact in self.contacts.iteritems():
            sent = self.construct_email_and_send(contact['email'])
            if not sent:
                _logger.debug('Error. Email could not be sent to [{0}]'.format(contact['email']))

    def send_message(self, name):
        """sends warning message (email) to contact with name

        returns:
            bool
        """
        success = True
        if not self.contacts.get(name):
            return not success
        contact = self.contacts.get(name)
        sent = self.construct_email_and_send(contact['email'])
        if not sent:
            _logger.debug('Error. Email could not be sent to [{0}]'.format(contact['email']))
            return not success

        return success


    def construct_email_and_send(self, email_addr):
        """constructs an HTML email and sends to specified recipient

        args:
            email: str

        returns:
            bool
        """
        success = True

        email = MIMEMultipart('alternative')
        email['Subject'] = PanicResponse._SYSTEM_EMAIL_SUBJECT.format(email)
        email['From'] = PanicResponse._SYSTEM_EMAIL
        email['To'] = email_addr

        # Create both plaintext and html version so that email application can render either when needed
        plaintext_version = "Plaintext version"
        html_version = "HTML version"
        plaintext = MIMEText(plaintext_version, 'plain')
        html = MIMEText(html_version, 'html')

        # Attach both plaintext and html to email
        email.attach(plaintext)
        email.attach(html)

        try:
            mail = smtplib.SMTP(PanicResponse._MAIL_SERVER, PanicResponse._MAIL_PORT)
            mail.ehlo()
            mail.starttls()
            mail.login(PanicResponse._SYSTEM_EMAIL, PanicResponse._SYSTEM_PASSWORD)
            mail.sendmail(email_addr, PanicResponse._SYSTEM_EMAIL, email.as_string())
            self.total_emails_sent += 1
        except smtplib.SMTPException as e:
            _logger.debug('Could not send email. [{0}]'.format(e))
            mail.quit()
            return not success

        mail.quit()
        return success
