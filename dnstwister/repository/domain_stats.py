"""Domain statistics repository."""
import datetime

from dnstwister import db
import dnstwister.storage.interfaces

# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def set_noise_stats(stats):
    """Update the stats for a domain."""
    key = 'statistics_noise:{}'.format(stats['domain'])
    value = {
        'deltas': stats['deltas'],
        'window_start': stats['window_start'].strftime('%Y-%m-%dT%H:%M:%SZ'),
        '__update': stats['__update'].strftime('%Y-%m-%dT%H:%M:%SZ'),
        '__increment': stats['__increment'].strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    db.set(key, value)


def get_noise_stats(domain):
    """Get the stats for a domain."""
    key = 'statistics_noise:{}'.format(domain)
    value = db.get(key)
    if value is None:
        return
    stats = {
        'domain': domain,
        'deltas': value['deltas'],
        'window_start': datetime.datetime.strptime(value['window_start'], '%Y-%m-%dT%H:%M:%SZ'),
        '__update': datetime.datetime.strptime(value['__update'], '%Y-%m-%dT%H:%M:%SZ'),
        '__increment': datetime.datetime.strptime(value['__increment'], '%Y-%m-%dT%H:%M:%SZ'),
    }
    return stats


def inoisy_domains():
    """Return an iterator of all the domains with noise stats."""
    domain_keys_iter = db.ikeys('statistics_noise')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('statistics_noise:')[1]
