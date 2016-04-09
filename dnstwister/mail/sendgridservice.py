"""SendGrid-based email sender.

The SendGrid service is attached to the Production web worker, but is
available to all workers.
"""
import os
import sendgrid


class SGSender(object):
    """Simple mail sender, using SendGrid."""
    def __init__(self, sender=None, username=None, password=None):
        self._sender = sender
        self._username = username
        self._password = password
        self._client = None
        self._setup_ran = False

    def _setup(self):
        if self._sender is None:
            self._sender = os.environ['EMAIL_FROM_ADDRESS']

        if self._username is None:
            self._username = os.environ['SENDGRID_USERNAME']

        if self._password is None:
            self._password = os.environ['SENDGRID_PASSWORD']

        self._client = sendgrid.SendGridClient(self._username, self._password)

    def send(self, to, subject, body):
        if not self._setup_ran:
            self._setup()
            self._setup_ran = True

        message = sendgrid.Mail()

        message.add_to(to)
        message.set_subject(subject)
        message.set_html(body)
        message.set_text(body)
        message.set_from(self._sender)

        return self._client.send(message)
