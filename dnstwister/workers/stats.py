"""Records stats about the system.
"""
import os
import time

import requests

from dnstwister.storage import stats_redis_store


def record_delta_stats(domain):
    """Record stats based on this domain."""
    stats_redis_store.note(domain)


def get_delta_domains():
    """Return a list of all the domains in all the delta reports."""
    json = requests.get(os.getenv('DELTAS_URL')).json
    return json['values']


def main():
    """Main code for worker."""
    while True:

        print 'Starting stats processing...'
        start = time.time()

        store = stats_redis_store.RedisStatsStore()
        for domain in get_delta_domains():
            store.note(domain)

        print 'All stats processed in {} seconds'.format(
            round(time.time() - start, 2)
        )
        time.sleep(60)


if __name__ == '__main__':
    main()
