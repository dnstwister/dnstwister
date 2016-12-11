"""Update the windows on all stats records."""
import time

from dnstwister.repository import domain_stats
from dnstwister.tools import noisy_domains


def process_domain(domain):
    """Update the window on this domain."""
    current_stats = domain_stats.get_noise_stats(domain)
    if current_stats is None:
        return
    updated_stats = noisy_domains.update(current_stats)
    domain_stats.set_noise_stats(updated_stats)


def main():
    """Main code for worker."""
    while True:

        domains_iter = domain_stats.inoisy_domains()

        while True:
            try:
                domain = domains_iter.next()
            except StopIteration:
                break

            process_domain(domain)

        print 'All stats windows updated'

        time.sleep(60)


if __name__ == '__main__':
    main()
