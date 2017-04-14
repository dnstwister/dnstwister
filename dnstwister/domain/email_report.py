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
        if self._new is not None and len(self._new) > 0:
            try:
                return [(domain, ip)
                        for (domain, ip)
                        in self._new
                        if domain not in self._noisy]
            except:
                import pdb; pdb.set_trace()

    @property
    def updated(self):
        """Return the updated non-noisy results we want to alert on."""
        if self._updated is not None and len(self._updated) > 0:
            return [(domain, ip1, ip2)
                    for (domain, ip1, ip2)
                    in self._updated
                    if domain not in self._noisy]

    @property
    def deleted(self):
        """Return the deleted non-noisy results we want to alert on."""
        if self._deleted is not None and len(self._deleted) > 0:
            return [domain
                    for domain
                    in self._deleted
                    if domain not in self._noisy]

    @property
    def noisy(self):
        """Return the noisy results."""
        if self._noisy is not None and len(self._noisy) > 0:
            return list(self._noisy)
