"""Domain statistics repository."""
import datetime

from dnstwister import stats_db as db
import dnstwister.storage.interfaces

from dnstwister.domain.statistics import NoiseStatistic

# Check the database we're using implements the interface.
dnstwister.storage.interfaces.instance_valid(db)


def mark_noise_stat_as_updated(domain, now=None):
    """Mark a set of statistics for a domain as updated."""
    if now is None:
        now = datetime.datetime.now()

    value = now.strftime(db.datetime_format)
    db.set('noise_statistic_updated', domain, value)


def noise_stat_last_updated(domain, now=None):
    """Get the last-updated date for the statistics for a domain."""
    if now is None:
        now = datetime.datetime.now()

    value = db.get('noise_statistic_updated', domain)
    if value is None:
        return

    return datetime.datetime.strptime(value, db.datetime_format)


def set_noise_stat(stat):
    """Update the noise statistics for a domain."""
    value = {
        'deltas': stat.deltas,
        'window_start': stat.window_start.strftime(db.datetime_format),
        'noisy': stat.is_noisy,
    }
    db.set('noise_statistic', stat.domain, value)


def get_noise_stat(domain):
    """Get the noise statistics for a domain."""
    stat = db.get('noise_statistic', domain)
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
    return db.ikeys('noise_statistic')
