"""Application repository."""
import datetime

import main
import storage.interfaces


# Check the database we're using implements the interface.
storage.interfaces.instance_valid(main.db)


def register_domain(domain):
    """Register a new domain for reporting.

    If the domain is already registered this is a no-op.
    """
    main.db.set('registered_for_reporting_{}'.format(domain), True)

def is_domain_registered(domain):
    """Return whether a domain is registered for reporting."""
    return main.db.get('registered_for_reporting_{}'.format(domain)) == True

def get_resolution_report(domain):
    """Retrieve the resolution report for a domain, or None."""
    return main.db.get('delta_report_{}'.format(domain))

def get_delta_report(domain):
    """Retrieve the delta report for a domain, or None."""
    return main.db.get('delta_report_{}'.format(domain))

def delta_report_updated(domain):
    """Retrieve when a delta report was last updated, or None."""
    return main.db.get('delta_report_updated_{}'.format(domain))

def update_delta(domain, delta=None, updated=None):
    """Update the delta report for a domain."""
    if delta is None:
        delta = {'new': [], 'updated': [], 'deleted': []}
    if updated is None:
        updated = datetime.datetime.now()
    main.db.set('delta_report_{}'.format(domain), delta)
    main.db.set('delta_report_updated_{}'.format(domain), updated)

def update_resolution_report(domain, report=None, updated=None):
    """Update the resolution report for a domain."""
    if report is None:
        report = {}
    if updated is None:
        updated = datetime.datetime.now()
    main.db.set('resolution_report_{}'.format(domain), report)
    main.db.set('resolution_report_updated_{}'.format(domain), updated)

def unregister_domain(domain):
    """Unregisters a domain from reporting.

    Unregistering a domain that isn't registered is a no-op.
    """
    main.db.delete('registered_for_reporting_{}'.format(domain))
