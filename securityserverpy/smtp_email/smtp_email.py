# -*- coding: utf-8 -*-
#
# email module
#

import os
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from securityserverpy import _logger

class Email(object):

    _MAIL_SERVER = 'smtp.gmail.com'
    _MAIL_PORT = 587
    _SYSTEM_EMAIL_ADDRESS = 'smart.vehicle.sec@gmail.com'
    _SYSTEM_PASSWORD = 'seniordesign2017'
    _SYSTEM_SUBJECT = 'Smart Vehicle Security Notification'

    def _send_email(self, html, email_addr):
        """sends an email

        args:
            html: str
            email_addr: str

        returns
            bool
        """
        email = MIMEMultipart('alternative')
        email['Subject'] = self._SYSTEM_SUBJECT
        email['From'] = self._SYSTEM_EMAIL_ADDRESS
        email['To'] = email_addr

        # Create both plaintext and html version so that email application can render either when needed
        plaintext_version = "Plaintext version"
        html_version = html
        plaintext = MIMEText(plaintext_version, 'plain')
        html = MIMEText(html_version, 'html')

        # Attach both plaintext and html to email
        email.attach(plaintext)
        email.attach(html)

        try:
            mail = smtplib.SMTP(self._MAIL_SERVER, self._MAIL_PORT)
            mail.ehlo()
            mail.starttls()
            mail.login(self._SYSTEM_EMAIL_ADDRESS, self._SYSTEM_PASSWORD)
            mail.sendmail(email_addr, self._SYSTEM_EMAIL_ADDRESS, email.as_string())
        except smtplib.SMTPException as e:
            _logger.debug('Could not send email. [{0}]'.format(e))
            mail.quit()
            return False

        mail.quit()
        return True

    def send_forgot_password_email(self, email_addr, new_password):
        """sends a forgot password email notification

        args:
            email_addr: str
            new_password: str

        returns:
            bool
        """
        html = "<h5>Here is your new temporary login information.</h5>" \
               "<p>Email: {0}</p><p>Password: {1}</p>".format(email_addr, new_password)
        return self._send_email(html, email_addr)

    def send_panic_response_email(self, email_addr, user):
        """sends panic response email notification

        args:
            email_addr: str
            user: {}

        returns:
            bool
        """
        html = "<h5>Here is a panic response email.</h5>" \
               "<p>You are a member of the emergency list of {0} {1}.</p>" \
               "<p>They initiated a panic response. Please get in contact with " \
               "them at -- {2} -- or get in contact with dispatchers.</p>".format(user['firstname'], user['lastname'], email_addr)
        return self._send_email(html, email_addr)