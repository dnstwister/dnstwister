"""Update the deltas on all stats records."""
import time

from dnstwister import repository
from dnstwister.repository import domain_stats
from dnstwister.tools import noisy_domains


def process_domain(domain):
    """Update the window on this domain."""
    delta_report = repository.get_delta_report(domain)
    if delta_report is None:
        return

    for results in delta_report.values():
        for result in results:
            result_domain = result[0]

            current_stats = domain_stats.get_noise_stats(result_domain)
            if current_stats is None:
                current_stats = noisy_domains.initialise_record(
                    result_domain, start=1
                )

            updated_stats = noisy_domains.increment(current_stats)
            domain_stats.set_noise_stats(updated_stats)


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
