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
    db.set('registered_for_reporting:{}'.format(domain), True)


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
        db.delete(':'.join((key, domain)))


def is_domain_registered(domain):
    """Return whether a domain is registered for reporting."""
    return db.get('registered_for_reporting:{}'.format(domain)) == True


def iregistered_domains():
    """Return an iterator of all the registered domains."""
    domain_keys_iter = db.ikeys('registered_for_reporting')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('registered_for_reporting:')[1]


def get_resolution_report(domain):
    """Retrieve the resolution report for a domain, or None."""
    return db.get('resolution_report:{}'.format(domain))


def get_delta_report(domain):
    """Retrieve the delta report for a domain, or None."""
    return db.get('delta_report:{}'.format(domain))


def delta_report_updated(domain):
    """Retrieve when a delta report was last updated, or None."""
    updated = db.get('delta_report_updated:{}'.format(domain))
    if updated is not None:
        return datetime.datetime.strptime(updated, '%Y-%m-%dT%H:%M:%SZ')


def update_delta_report(domain, delta=None, updated=None):
    """Update the delta report for a domain."""
    if delta is None:
        delta = {'new': [], 'updated': [], 'deleted': []}
    if updated is None:
        updated = datetime.datetime.now()
    db.set('delta_report:{}'.format(domain), delta)
    db.set(
        'delta_report_updated:{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def mark_delta_report_as_read(domain, last_read=None):
    """Update the "last-read" date for delta report."""
    if last_read is None:
        last_read = datetime.datetime.now()
    db.set(
        'delta_report_read:{}'.format(domain),
        last_read.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def delta_report_last_read(domain):
    """Retrieve the "last-read" date for delta report."""
    last_read = db.get('delta_report_read:{}'.format(domain))
    if last_read is not None:
        return datetime.datetime.strptime(last_read, '%Y-%m-%dT%H:%M:%SZ')


def update_resolution_report(domain, report=None, updated=None):
    """Update the resolution report for a domain."""
    if report is None:
        report = {}
    if updated is None:
        updated = datetime.datetime.now()
    db.set('resolution_report:{}'.format(domain), report)
    db.set(
        'resolution_report_updated:{}'.format(domain),
        updated.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def isubscriptions():
    """Return an iterator of subscription information."""
    keys_iter = db.ikeys('email_sub')
    while True:
        key = keys_iter.next()
        if key is not None and not key.startswith('email_sub_pending_'):
            sub = db.get(key)
            if sub is not None:
                yield key.split('email_sub:')[1], sub


def propose_subscription(verify_code, email_address, domain):
    """Store that a sub has been proposed (pending email verification)."""
    db.set(
        'email_sub_pending:{}'.format(verify_code), {
            'email_address': email_address,
            'domain': domain,
            'since': datetime.datetime.now().strftime(
                '%Y-%m-%dT%H:%M:%SZ'
            ),
        }
    )


def get_proposition(verify_code):
    """Retrieve the proposition for a verify code (or None)."""
    return db.get('email_sub_pending:{}'.format(verify_code))


def remove_proposition(verify_code):
    """Remove an existing proposition."""
    db.delete('email_sub_pending:{}'.format(verify_code))


def subscribe_email(sub_id, email_address, domain):
    """Add a subscription for an email to a domain."""
    db.set('email_sub:{}'.format(sub_id), {
        'email_address': email_address,
        'domain': domain,
    })


def update_last_email_sub_sent_date(sub_id):
    """Note that an email has been sent for a subscription."""
    db.set(
        'email_sub_last_sent:{}'.format(sub_id),
        datetime.datetime.now().strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
    )


def email_last_send_for_sub(sub_id):
    """Return when an email was last sent for a subscription, or None."""
    last_sent = db.get('email_sub_last_sent:{}'.format(sub_id))
    if last_sent is not None:
        return datetime.datetime.strptime(last_sent, '%Y-%m-%dT%H:%M:%SZ')


def unsubscribe(sub_id):
    """Unsubscribe a user."""
    db.delete('email_sub:{}'.format(sub_id))
