"""View model for rendering the email template."""


class EmailReport(object):
    """View model for the email template."""
    def __init__(self, new, updated, deleted, noisy):
        self._new = new
        self._updated = updated
        self._deleted = deleted
        self._noisy = noisy

    @property
    def new(self):
        """Return the new non-noisy results we want to alert on."""
        return [(domain, ip)
                for (domain, ip)
                in self._new
                if domain not in self._noisy]

    @property
    def updated(self):
        """Return the updated non-noisy results we want to alert on."""
        return [(domain, ip1, ip2)
                for (domain, ip1, ip2)
                in self._updated
                if domain not in self._noisy]

    @property
    def deleted(self):
        """Return the deleted non-noisy results we want to alert on."""
        return [domain
                for domain
                in self._deleted
                if domain not in self._noisy]

    @property
    def noisy(self):
        """Return the noisy results."""
        return list(self._noisy)
