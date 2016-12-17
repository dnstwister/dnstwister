"""Domain statistics repository."""
import datetime

from dnstwister import db
import dnstwister.storage.interfaces

from dnstwister.domain.statistics import NoiseStatistic

# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def mark_noise_stat_as_updated(domain, now=None):
    """Mark a set of statistics for a domain as updated."""
    if now is None:
        now = datetime.datetime.now()

    key = 'noise_statistic_updated:{}'.format(domain)
    value = now.strftime(db.datetime_format)
    db.set(key, value)


def noise_stat_last_updated(domain, now=None):
    """Get the last-updated date for the statistics for a domain."""
    if now is None:
        now = datetime.datetime.now()

    key = 'noise_statistic_updated:{}'.format(domain)
    value = db.get(key)
    if value is None:
        return

    return datetime.datetime.strptime(value, db.datetime_format)


def set_noise_stat(stat):
    """Update the noise statistics for a domain."""
    key = 'noise_statistic:{}'.format(stat.domain)
    value = {
        'deltas': stat.deltas,
        'window_start': stat.window_start.strftime(db.datetime_format),
        'noisy': stat.is_noisy,
    }
    db.set(key, value)


def get_noise_stat(domain):
    """Get the noise statistics for a domain."""
    key = 'noise_statistic:{}'.format(domain)
    stat = db.get(key)
    if stat is None:
        return

    return NoiseStatistic(
        domain,
        stat['deltas'],
        datetime.datetime.strptime(stat['window_start']),
        stat['noisy'],
    )


def inoisy_domains():
    """Return an iterator of all the domains with noise statistics."""
    domain_keys_iter = db.ikeys('noise_statistic')
    while True:
        domain_key = domain_keys_iter.next()
        if domain_key is not None:
            yield domain_key.split('noise_statistic:')[1]
