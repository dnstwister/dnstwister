"""Application repository."""
import datetime

from dnstwister import data_db as db
import dnstwister.storage.interfaces


# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def register_domain(domain):
    """Register a new domain for reporting.

    If the domain is already registered this is a no-op.
    """
    db.set('registered_for_reporting', domain, True)


def unregister_domain(domain):
    """Unregisters a domain from reporting.

    Unregistering a domain that isn't registered is a no-op.
    """
    prefixes = (
        'registered_for_reporting',
        'resolution_report',
        'resolution_report_updated',
        'delta_report',
        'delta_report_updated',
        'delta_report_read',
    )
    for prefix in prefixes:
        db.delete(prefix, domain)


def is_domain_registered(domain):
    """Return whether a domain is registered for reporting."""
    return db.get('registered_for_reporting', domain) is True


def iregistered_domains():
    """Return an iterator of all the registered domains."""
    return db.ikeys('registered_for_reporting')


def get_resolution_report(domain):
    """Retrieve the resolution report for a domain, or None."""
    return db.get('resolution_report', domain)


def get_delta_report(domain):
    """Retrieve the delta report for a domain, or None."""
    return db.get('delta_report', domain)


def delta_report_updated(domain):
    """Retrieve when a delta report was last updated, or None."""
    updated = db.get('delta_report_updated', domain)
    if updated is not None:
        return db.from_db_datetime(updated)


def update_delta_report(domain, delta, updated=None):
    """Update the delta report for a domain."""
    if updated is None:
        updated = datetime.datetime.now()
    db.set('delta_report', domain, delta)
    db.set('delta_report_updated', domain, db.to_db_datetime(updated))


def mark_delta_report_as_read(domain, last_read=None):
    """Update the "last-read" date for delta report."""
    if last_read is None:
        last_read = datetime.datetime.now()
    db.set('delta_report_read', domain, db.to_db_datetime(last_read))


def delta_report_last_read(domain):
    """Retrieve the "last-read" date for delta report."""
    last_read = db.get('delta_report_read', domain)
    if last_read is not None:
        return db.from_db_datetime(last_read)


def update_resolution_report(domain, report, updated=None):
    """Update the resolution report for a domain."""
    if updated is None:
        updated = datetime.datetime.now()
    db.set('resolution_report', domain, report)
    db.set(
        'resolution_report_updated',
        domain,
        db.to_db_datetime(updated)
    )


def isubscriptions():
    """Return an iterator of subscription information."""
    keys_iter = db.ikeys('email_sub')
    while True:
        key = keys_iter.next()
        if key is not None:
            sub = db.get('email_sub', key)
            if sub is not None:
                yield key, sub


def propose_subscription(verify_code, email_address, domain):
    """Store that a sub has been proposed (pending email verification)."""
    db.set(
        'email_sub_pending', verify_code, {
            'email_address': email_address,
            'domain': domain,
            'since': db.to_db_datetime(datetime.datetime.now()),
        }
    )


def get_proposition(verify_code):
    """Retrieve the proposition for a verify code (or None)."""
    return db.get('email_sub_pending', verify_code)


def remove_proposition(verify_code):
    """Remove an existing proposition."""
    db.delete('email_sub_pending', verify_code)


def subscribe_email(sub_id, email_address, domain):
    """Add a subscription for an email to a domain."""
    db.set('email_sub', sub_id, {
        'email_address': email_address,
        'domain': domain,
    })


def update_last_email_sub_sent_date(sub_id, when=None):
    """Note that an email has been sent for a subscription."""
    if when is None:
        when = datetime.datetime.now()
    db.set(
        'email_sub_last_sent', sub_id,
        db.to_db_datetime(when)
    )


def email_last_send_for_sub(sub_id):
    """Return when an email was last sent for a subscription, or None."""
    last_sent = db.get('email_sub_last_sent', sub_id)
    if last_sent is not None:
        return db.from_db_datetime(last_sent)


def unsubscribe(sub_id):
    """Unsubscribe a user."""
    db.delete('email_sub', sub_id)
    db.delete('email_sub_last_sent', sub_id)
