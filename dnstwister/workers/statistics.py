"""Update the deltas on all statistics records."""
import datetime
import time

from dnstwister import repository
from dnstwister.tools import delta_reports
from dnstwister.domain.statistics import NoiseStatistic
from dnstwister.repository import statistics as statistics_repository


FREQUENCY = datetime.timedelta(days=1)


def process_domain(registered_domain, updated_domains=None, now=None):
    """Update the statistics for all fuzz results for this domain."""
    if now is None:
        now = datetime.datetime.now()

    if updated_domains is None:
        updated_domains = set()
    else:
        updated_domains = set(updated_domains)

    delta_report = repository.get_delta_report(registered_domain)
    if delta_report is None:
        return updated_domains

    for domain in delta_reports.extract_domains(delta_report):

        if domain in updated_domains:
            continue

        updated = statistics_repository.noise_stat_last_updated(domain)
        if updated is not None and (now - updated) < FREQUENCY:
            continue

        stat = statistics_repository.get_noise_stat(domain)
        if stat is None:
            stat = NoiseStatistic(domain, deltas=1)
        else:
            stat.increment()
            stat.update_window()

        statistics_repository.set_noise_stat(stat)
        statistics_repository.mark_noise_stat_as_updated(domain)
        updated_domains.add(domain)

    return updated_domains


def increment_delta_report_domains():
    """Add/increment domains found in delta reports.

    Return set of domains updated found.
    """
    updated_domains = set()
    domains_iter = repository.iregistered_domains()

    while True:
        try:
            domain = domains_iter.next()
        except StopIteration:
            break

        updated_domains = process_domain(domain, updated_domains)

    return updated_domains


def update_remaining_stats(updated_domains, now=None):
    """Update the last checked date on domains not already updated."""
    if now is None:
        now = datetime.datetime.now()

    updated_domains = set()
    domains_iter = statistics_repository.inoisy_domains()

    while True:
        try:
            domain = domains_iter.next()
        except StopIteration:
            break

        if domain in updated_domains:
            continue

        updated = statistics_repository.noise_stat_last_updated(domain)
        if updated is not None and (now - updated) < FREQUENCY:
            continue

        statistics_repository.mark_noise_stat_as_updated(domain)
        updated_domains.add(domain)

    return updated_domains


def main():
    """Main code for worker."""
    while True:

        incremented_domains = increment_delta_report_domains()
        print 'Incremented statistic for {} domains.'.format(
            len(incremented_domains)
        )

        updated_domains = update_remaining_stats(incremented_domains)
        print 'Marked {} domains\' statistics as up to date.'.format(
            len(updated_domains)
        )

        time.sleep(60)


if __name__ == '__main__':
    main()
