"""Update the deltas on all statistics records."""
import datetime
import time

from dnstwister import repository
from dnstwister.tools import delta_reports
from dnstwister.domain.statistics import NoiseStatistic
from dnstwister.repository import statistics as statistics_repository


FREQUENCY = datetime.timedelta(days=1)


def process_domain(registered_domain, updated_domains, now=None):
    """Update the statistics for all fuzz results for this domain."""
    if now is None:
        now = datetime.datetime.now()

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


def increment_email_sub_deltas():
    """Add/increment domains found in delta reports for email subs.

    Return count of updated domains.
    """
    updated_domains = set()
    subs_iter = repository.isubscriptions()

    while True:
        try:
            sub = subs_iter.next()
        except StopIteration:
            break

        sub_detail = sub[1]
        domain = sub_detail['domain']

        updated_domains = process_domain(domain, updated_domains)

    return len(updated_domains)


def main():
    """Main code for worker."""
    while True:

        start = time.time()
        incremented_count = increment_email_sub_deltas()
        print 'Incremented stats for {} domains in {} seconds.'.format(
            incremented_count,
            round(time.time() - start, 2)
        )

        time.sleep(60)


if __name__ == '__main__':
    main()
