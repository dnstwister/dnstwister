"""Records stats about the system.

This worker is fired from a Heroku schedule and requires an external data
source returning data to function correctly, something that is not part of the
GitHub repository.
"""
import os
import time

import requests

from dnstwister import dnstwist
from dnstwister.storage import redis_stats_store


def get_delta_domains():
    """Return a list of all the domains in all the delta reports.

    If this stops scaling I'll switch to an iterator off a DB query.
    """
    url = os.getenv('DELTAS_URL')
    if url is None:
        raise Exception('Delta report URL configuration not set!')

    json = requests.get(url, timeout=10).json()
    return [domain
            for (domain,)
            in json['values']
            if dnstwist.is_valid_domain(domain)]


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
