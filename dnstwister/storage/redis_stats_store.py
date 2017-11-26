"""Trivial redis store for domains.

Will be used to store a 7-day sliding window count of domains appearing in
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

        url = os.getenv('REDIS_URL')
        if url is None:
            raise Exception('REDIS connection configuration not set!')
        self._url = url

    @property
    def r_conn(self):
        """I am a redis connection!!!"""
        if self._conn is None:
            self._conn = redis.from_url(self._url)
        return self._conn

    def note(self, domain):
        """Record that the domains have appeared in a delta report.

        We increment each time we note, and move the expiry forward to the
        chosen number of seconds. That gives us a sliding window of changes
        over the period.
        """
        if dnstwist.validate_domain(domain):
            pipe = self.r_conn.pipeline()
            pipe.incr(domain)
            pipe.expire(domain, EXPIRY)
            pipe.execute()

    def is_noisy(self, domain, threshold=3):
        """A domain is noisy if it changes more than threshold times over the
        expiry window.
        """
        score = self.r_conn.get(domain)
        if score is None:
            return False
        return int(score) > threshold
