"""Application repository."""
import datetime

import main
import storage.interfaces


class Repository(object):
    """Application repository to handle domain activities."""
    def __init__(self, db=main.db):
        if storage.interfaces.instance_valid(db):
            self._db = db

    def register_domain(self, domain):
        """Register a new domain for reporting.

        If the domain is already registered this is a no-op.
        """
        self._db.set('registered_for_reporting_{}'.format(domain), True)

    def is_domain_registered(self, domain):
        """Return whether a domain is registered for reporting."""
        return self._db.get(
            'registered_for_reporting_{}'.format(domain) == True
        )

    def get_resolution_report(self, domain):
        """Retrieve the resolution report for a domain, or None."""
        return self._db.get('delta_report_{}'.format(domain))

    def get_delta_report(self, domain):
        """Retrieve the delta report for a domain, or None."""
        return self._db.get('delta_report_{}'.format(domain))

    def delta_report_updated(self, domain):
        """Retrieve when a delta report was last updated, or None."""
        return self._db.get('delta_report_updated_{}'.format(domain))

    def update_delta(self, domain, delta=None, updated=None):
        """Update the delta report for a domain."""
        if delta is None:
            delta = {'new': [], 'updated': [], 'deleted': []}
        if updated is None:
            updated = datetime.datetime.now()
        self._db.set('delta_report_{}'.format(domain), delta)
        self._db.set('delta_report_updated_{}'.format(domain), updated)

    def update_resolution_report(self, domain, report=None, updated=None):
        """Update the resolution report for a domain."""
        if report is None:
            report = {}
        if updated is None:
            updated = datetime.datetime.now()
        self._db.set('resolution_report_{}'.format(domain), report)
        self._db.set('resolution_report_updated_{}'.format(domain), updated)

    def unregister_domain(self, domain):
        """Unregisters a domain from reporting.

        Unregistering a domain that isn't registered is a no-op.
        """
        self._db.delete('registered_for_reporting_{}'.format(domain))
