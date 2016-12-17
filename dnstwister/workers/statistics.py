"""Update the deltas on all statistics records."""
import datetime
import time

from dnstwister import repository
from dnstwister.tools import delta_reports
from dnstwister.domain.statistics import NoiseStatistic
from dnstwister.repository import statistics as statistics_repository


FREQUENCY = datetime.timedelta(days=1)


def process_domain(registered_domain, now=None):
    """Update the statistics for all fuzz results for this domain."""
    if now is None:
        now = datetime.datetime.now()

    delta_report = repository.get_delta_report(registered_domain)
    if delta_report is None:
        return

    for domain in delta_reports.extract_domains(delta_report):

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


def main():
    """Main code for worker."""
    while True:

        domains_iter = repository.iregistered_domains()

        while True:
            try:
                domain = domains_iter.next()
            except StopIteration:
                break

            process_domain(domain)

        print 'All statistics for all deltas processed'

        time.sleep(60)


if __name__ == '__main__':
    main()
