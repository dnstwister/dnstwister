"""SendGrid-based email sender.

The SendGrid service is attached to the Production web worker, but is
available to all workers.

All email-managing workers need the following environ keys:

    SENDGRID_PASSWORD
    SENDGRID_USERNAME
    EMAIL_FROM_NAME
    EMAIL_FROM_ADDRESS

"""
import os
import sendgrid


class SGSender(object):
    """Simple mail sender, using SendGrid."""
    def __init__(self, sender=None, sender_name=None, username=None,
                 password=None):
        self._sender = sender
        self._sender_name = sender_name
        self._username = username
        self._password = password
        self._client = None
        self._setup_ran = False

    def _setup(self):
        if self._sender is None:
            self._sender = os.environ['EMAIL_FROM_ADDRESS']

        if self._sender_name is None:
            self._sender_name = os.environ['EMAIL_FROM_NAME']

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
        message.set_from_name(self._sender_name)

        return self._client.send(message)
