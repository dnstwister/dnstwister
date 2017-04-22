"""Model for the email template, acts as domain and view model."""


class EmailReport(object):
    """View model for the email template."""
    def __init__(self, delta_report, noisy_domains, include_noisy_domains):
        self._new = tuple([(dom, ip)
                           for (dom, ip)
                           in delta_report['new']
                           if dom not in noisy_domains])

        self._updated = tuple([(dom, ip1, ip2)
                               for (dom, ip1, ip2)
                               in delta_report['updated']
                               if dom not in noisy_domains])

        self._deleted = tuple([dom
                               for dom
                               in delta_report['deleted']
                               if dom not in noisy_domains])

        self._noisy = tuple(noisy_domains if include_noisy_domains else [])

    @property
    def new(self):
        """Return the new non-noisy results we want to alert on."""
        return self._new

    @property
    def updated(self):
        """Return the updated non-noisy results we want to alert on."""
        return self._updated

    @property
    def deleted(self):
        """Return the deleted non-noisy results we want to alert on."""
        return self._deleted

    @property
    def noisy(self):
        """Return the noisy results."""
        return self._noisy

    def has_results(self):
        """Are there any results to render?"""
        results = (
            len(self.new) +
            len(self.updated) +
            len(self.deleted) +
            len(self.noisy)
        )
        return results > 0
