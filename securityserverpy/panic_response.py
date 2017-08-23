import os
import os.path
import yaml

from securityserverpy import _logger


class PanicResponse(object):
    """handles panic response communication to selected contacts given by client

    With this module, we will be able to send text messages and emails to selected contacts
    when a bad alert is happening or when the panic button is pressed by someone in the vehicle
    """

    _DEFAULT_FILE = 'yamls/contacts.yaml'
    _CONTACTS_INDEX = 'contacts'
    _CONTACT_LIMIT = 15

    def __init__(self, file_name=None):
        self.contacts = {}
        self.local_file_name = file_name or PanicResponse._DEFAULT_FILE
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
        """sends warning message (email) to all contacts

        returns:
            bool
        """
        pass

    def send_message(self, name):
        """sends warning message (email) to contact with name

        returns:
            bool
        """
        pass


