"""Domain statistics repository."""
from dnstwister import db
import dnstwister.storage.interfaces

# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def set_noise_stats(stats):
    """Update the stats for a domain."""
    stats = dict(stats)
    key = 'statistics_noise:{}'.format(stats['domain'])
    del stats['domain']
    db.set(key, stats)


def get_noise_stats(domain):
    """Get the stats for a domain."""
    key = 'statistics_noise:{}'.format(domain)
    stats = db.get(key)
    if stats is None:
        return
    stats = dict(stats)
    stats['domain'] = domain
    return stats


def inoisy_domains():
    """Return an iterator of all the domains with noise stats."""
    domain_keys_iter = db.ikeys('statistics_noise')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('statistics_noise:')[1]
