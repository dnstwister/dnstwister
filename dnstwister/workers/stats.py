"""Update the deltas on all stats records."""
import datetime
import time

from dnstwister import repository
from dnstwister.repository import domain_stats as stats_repo
from dnstwister.tools import noisy_domains


def _extract_domains(delta_report):
    """Return the domains in a delta report."""
    return (
        [d[0] for d in delta_report['new']] +
        [d[0] for d in delta_report['updated']] +
        delta_report['deleted']
    )


def process_domain(registered_domain, now=None):
    """Update the stats for all fuzz results for this domain."""
    if now is None:
        return datetime.datetime.now()

    delta_report = repository.get_delta_report(registered_domain)
    if delta_report is None:
        return

    for domain in _extract_domains(delta_report):

        stats_updated = stats_repo.noise_stats_last_updated(domain)

        if stats_updated is not None and (now - stats_updated).days < 1:
            continue

        stats = stats_repo.get_noise_stats(domain)

        if stats is None:
            stats = noisy_domains.initialise_record(domain)

        stats = noisy_domains.increment(stats)
        stats = noisy_domains.update_window(stats)
        stats = noisy_domains.update_noisy_flag(stats)

        stats_repo.set_noise_stats(stats)
        stats_repo.mark_noise_stats_as_updated(domain)


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

        print 'All stats for all deltas processed'

        time.sleep(60)


if __name__ == '__main__':
    main()
