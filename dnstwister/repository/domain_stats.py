"""Domain statistics repository."""
import datetime

from dnstwister import db
import dnstwister.storage.interfaces

# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def mark_noise_stats_as_updated(domain, now=None):
    """Mark a set of stats for a domain as updated."""
    if now is None:
        now = datetime.datetime.now()

    key = 'noise_statistics_updated:{}'.format(domain)
    value = now.strftime(db.datetime_format)
    db.set(key, value)


def noise_stats_last_updated(domain, now=None):
    """Get the last-updated date for the stats for a domain."""
    if now is None:
        now = datetime.datetime.now()

    key = 'noise_statistics_updated:{}'.format(domain)
    value = db.get(key)
    if value is None:
        return

    return datetime.datetime.strptime(value, db.datetime_format)


def set_noise_stats(stats):
    """Update the noise stats for a domain."""
    key = 'noise_statistics:{}'.format(stats['domain'])
    value = {
        'deltas': stats['deltas'],
        'window_start': stats['window_start'].strftime(db.datetime_format),
        'noisy': stats['noisy'],
    }
    db.set(key, value)


def get_noise_stats(domain):
    """Get the noise stats for a domain."""
    key = 'noise_statistics:{}'.format(domain)
    value = db.get(key)
    if value is None:
        return
    stats = {
        'domain': domain,
        'deltas': value['deltas'],
        'window_start': datetime.datetime.strptime(value['window_start'], db.datetime_format),
        'noisy': value['noisy'],
    }

    return stats


def inoisy_domains():
    """Return an iterator of all the domains with noise stats."""
    domain_keys_iter = db.ikeys('noise_statistics')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('noise_statistics:')[1]
