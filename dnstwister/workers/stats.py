"""Records stats about the system."""
import os
import time

import requests

from dnstwister import dnstwist
from dnstwister.storage import redis_stats_store


def get_delta_domains(url=os.getenv('DELTAS_URL')):
    """Return a list of all the domains in all the delta reports.

    If this stops scaling I'll switch to an iterator off a DB query.
    """
    if url is None:
        raise Exception('Delta report URL configuration not set!')

    json = requests.get(url, timeout=10).json()
    return [domain
            for (domain,)
            in json['values']
            if dnstwist.validate_domain(domain)]


def main():
    """Main code for worker.

    Run as often as like on a schedule.

    I'm doing it via a Heroku scheduler calling:

        python -m dnstwister.workers.stats

    """
    start = time.time()
    store = redis_stats_store.RedisStatsStore()

    delta_domains = get_delta_domains()
    for domain in delta_domains:
        store.note(domain)

    print 'Processed stats for {} domains in {} seconds'.format(
        len(delta_domains),
        round(time.time() - start, 2)
    )


if __name__ == '__main__':
    main()
