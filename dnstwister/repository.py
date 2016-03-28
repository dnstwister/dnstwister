"""Application repository."""
import datetime

from dnstwister import db
import storage.interfaces


# Check the database we're using implements the interface.
storage.interfaces.instance_valid(db)


def register_domain(domain):
    """Register a new domain for reporting.

    If the domain is already registered this is a no-op.
    """
    db.set('registered_for_reporting_{}'.format(domain), True)


def unregister_domain(domain):
    """Unregisters a domain from reporting.

    Unregistering a domain that isn't registered is a no-op.
    """
    keys = (
        'registered_for_reporting',
        'resolution_report',
        'resolution_report_updated',
        'delta_report',
        'delta_report_updated',
        'delta_report_read',
    )
    for key in keys:
        db.delete('_'.join((key, domain)))


def is_domain_registered(domain):
    """Return whether a domain is registered for reporting."""
    return db.get('registered_for_reporting_{}'.format(domain)) == True


def iregistered_domains():
    """Return an iterator of all the registered domains."""
    domain_keys_iter = db.ikeys('registered_for_reporting_')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('registered_for_reporting_')[1]


def get_resolution_report(domain):
    """Retrieve the resolution report for a domain, or None."""
    return db.get('resolution_report_{}'.format(domain))


def get_delta_report(domain):
    """Retrieve the delta report for a domain, or None."""
    return db.get('delta_report_{}'.format(domain))


def delta_report_updated(domain):
    """Retrieve when a delta report was last updated, or None."""
    updated = db.get('delta_report_updated_{}'.format(domain))
    if updated is not None:
        return datetime.datetime.strptime(updated, '%Y-%m-%dT%H:%M:%SZ')


def update_delta_report(domain, delta=None, updated=None):
    """Update the delta report for a domain."""
    if delta is None:
        delta = {'new': [], 'updated': [], 'deleted': []}
    if updated is None:
        updated = datetime.datetime.now()
    db.set('delta_report_{}'.format(domain), delta)
    db.set(
        'delta_report_updated_{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def mark_delta_report_as_read(domain, last_read=None):
    """Update the "last-read" date for delta report."""
    if last_read is None:
        last_read = datetime.datetime.now()
    db.set(
        'delta_report_read_{}'.format(domain),
        last_read.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def delta_report_last_read(domain):
    """Retrieve the "last-read" date for delta report."""
    last_read = db.get('delta_report_read_{}'.format(domain))
    if last_read is not None:
        return datetime.datetime.strptime(last_read, '%Y-%m-%dT%H:%M:%SZ')


def update_resolution_report(domain, report=None, updated=None):
    """Update the resolution report for a domain."""
    if report is None:
        report = {}
    if updated is None:
        updated = datetime.datetime.now()
    db.set('resolution_report_{}'.format(domain), report)
    db.set(
        'resolution_report_updated_{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def isubscriptions(list_all=False):
    """Return an iterator of verified subscriptions for domains."""
    keys_iter = db.ikeys('email_sub_')
    while True:
        key = keys_iter.next()
        if key is not None:
            sub = db.get(key)
            if sub is not None and (list_all or sub['domain'] is not None):
                yield key.split('email_sub_')[1], sub


def stage_email_subscription(email, verify_code):
    """Prepare an email subscription."""
    db.set('email_sub_{}'.format(verify_code), {
        'email': email,
        'created': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'last_sent': None,
        'domain': None,
    })


def verify_code_valid(verify_code):
    """Returns whether a verify code is valid or not."""
    return db.get('email_sub_{}'.format(verify_code)) is not None


def subscribe_email(verify_code, domain):
    """Add a subscription for an email to a domain."""
    subscription = db.get('email_sub_{}'.format(verify_code))

    if subscription['domain'] is None:
        subscription['domain'] = domain

    db.set('email_sub_{}'.format(verify_code), subscription)

    register_domain(domain)
