"""Trivial redis store for domains.

Will be used to store a 7-day "sliding window" count of domains appearing in
delta reports.

Reads from Heroku Dataclip of domains in delta reports, writes to Redis.

Dataclip is:

    select distinct delta_value->>0 as domain
    from (
      select
        json_array_elements(data.value::json->'new') as delta_value
      from data
      union all
      select
        json_array_elements(data.value::json->'updated') as delta_value
      from data
      union all
      select
        json_array_elements(data.value::json->'deleted') as delta_value
      from data
    ) as delta_values
    where delta_value->>0 != 'null'

Note: The window is a bit fuzzy on the definition of "sliding". If the domain
does not change in 7 days, then it will be removed, so would be considered
not noisy. In the first 7 days it must change "threshold" times to be noisy
then after that it only needs to change once every 7 days to remain noisy.

This is a form of hysteresis caused by the simplicity I want to use for redis
storage.
"""
import datetime
import os

import redis

from dnstwister import dnstwist


EXPIRY = int(datetime.timedelta(days=7).total_seconds())


class RedisStatsStore(object):
    """The store for the statistics."""
    def __init__(self):
        self._conn = None

    @property
    def r_conn(self):
        """I am a redis connection!!!"""
        if self._conn is None:
            url = os.getenv('REDIS_URL')
            if url is None:
                raise Exception('REDIS connection configuration not set!')
            self._conn = redis.from_url(url)
        return self._conn

    def note(self, domain):
        """Record that the domains have appeared in a delta report.

        We increment each time we note, and move the expiry forward to the
        chosen number of seconds. That gives us a sliding window of changes
        over the period.
        """
        if dnstwist.is_valid_domain(domain):
            pipe = self.r_conn.pipeline()
            pipe.incr(domain)
            pipe.expire(domain, EXPIRY)
            pipe.execute()

    def is_noisy(self, domain, threshold=4):
        """A domain is noisy if it changes more than threshold times over the
        expiry window.

        Domains not in the redis store return None, which becomes threshold,
        so that they are always false.
        """
        score = self.r_conn.get(domain)
        return int(score or threshold) > threshold
