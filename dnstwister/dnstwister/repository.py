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
        main.db.delete('_'.join((key, domain)))


def is_domain_registered(domain):
    """Return whether a domain is registered for reporting."""
    return main.db.get('registered_for_reporting_{}'.format(domain)) == True


def iregistered_domains():
    """Return an iterator of all the registered domains."""
    domain_keys_iter = main.db.ikeys('registered_for_reporting_')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('registered_for_reporting_')[1]


def get_resolution_report(domain):
    """Retrieve the resolution report for a domain, or None."""
    return main.db.get('resolution_report_{}'.format(domain))


def get_delta_report(domain):
    """Retrieve the delta report for a domain, or None."""
    return main.db.get('delta_report_{}'.format(domain))


def delta_report_updated(domain):
    """Retrieve when a delta report was last updated, or None."""
    updated = main.db.get('delta_report_updated_{}'.format(domain))
    if updated is not None:
        return datetime.datetime.strptime(updated, '%Y-%m-%dT%H:%M:%SZ')


def update_delta_report(domain, delta=None, updated=None):
    """Update the delta report for a domain."""
    if delta is None:
        delta = {'new': [], 'updated': [], 'deleted': []}
    if updated is None:
        updated = datetime.datetime.now()
    main.db.set('delta_report_{}'.format(domain), delta)
    main.db.set(
        'delta_report_updated_{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def mark_delta_report_as_read(domain, last_read=None):
    """Update the "last-read" date for delta report."""
    if last_read is None:
        last_read = datetime.datetime.now()
    main.db.set(
        'delta_report_read_{}'.format(domain),
        last_read.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def delta_report_last_read(domain):
    """Retrieve the "last-read" date for delta report."""
    last_read = main.db.get('delta_report_read_{}'.format(domain))
    if last_read is not None:
        return datetime.datetime.strptime(last_read, '%Y-%m-%dT%H:%M:%SZ')


def update_resolution_report(domain, report=None, updated=None):
    """Update the resolution report for a domain."""
    if report is None:
        report = {}
    if updated is None:
        updated = datetime.datetime.now()
    main.db.set('resolution_report_{}'.format(domain), report)
    main.db.set(
        'resolution_report_updated_{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def stage_email_subscription(email, verify_code):
    """Prepare an email subscription."""
    main.db.set('email_id_{}'.format(verify_code), {
        'email': email,
        'subs': [],
    })


def verify_code_valid(verify_code):
    """Returns whether a verify code is valid or not."""
    return main.db.get('email_id_{}'.format(verify_code)) is not None


def subscribe_email(verify_code, domain):
    """Add a subscription for an email to a domain."""
    subscription = main.db.get('email_id_{}'.format(verify_code))

    if domain not in subscription['subs']:
        subscription['subs'].append(domain)

    main.db.set('email_id_{}'.format(verify_code), subscription)

    register_domain(domain)
