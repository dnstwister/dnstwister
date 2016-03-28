import os
import sendgrid


class SGSender(object):
    """Simple mail sender, using SendGrid."""
    def __init__(self, sender=None, username=None, password=None):
        if sender is None:
            sender = os.environ['EMAIL_FROM_ADDRESS']

        if username is None:
            username = os.environ['SENDGRID_USERNAME']

        if password is None:
            password = os.environ['SENDGRID_PASSWORD']

        self._sender = sender
        self._client = sendgrid.SendGridClient(username, password)

    def send(self, to, subject, body):
        message = sendgrid.Mail()

        message.add_to(to)
        message.set_subject(subject)
        message.set_text(body)
        message.set_from(self._sender)

        return self._client.send(message)
