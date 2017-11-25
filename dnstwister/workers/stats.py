"""Records stats about the system."""
import datetime
import os
import time

import requests

from dnstwister import dnstwist
from dnstwister.storage import redis_stats_store


CADENCE = datetime.timedelta(hours=24)


def get_delta_domains():
    """Return a list of all the domains in all the delta reports."""
    json = requests.get(os.getenv('DELTAS_URL'), timeout=10).json()
    return [domain
            for (domain,)
            in json['values']
            if dnstwist.validate_domain(domain)]


def main():
    """Main code for worker."""
    while True:

        start = time.time()

        store = redis_stats_store.RedisStatsStore()

        last_run = store.last_time_all_noted()
        age = datetime.datetime.now() - last_run
        if age < CADENCE:
            sleep_time = (CADENCE - age).total_seconds()
            time.sleep(sleep_time)
            continue

        delta_domains = get_delta_domains()
        for domain in delta_domains:
            store.note(domain)
        store.all_noted()

        print 'Processed {} in {} seconds'.format(
            len(delta_domains),
            round(time.time() - start, 2)
        )


if __name__ == '__main__':
    main()
