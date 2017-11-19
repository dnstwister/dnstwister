"""Trivial redis store for domains.

Will be used to store a 7-day sliding window count of domains appearing in
delta reports.

Reads from Heroku Dataclip of domains in delta reports, writes to Redis.

Dataclip is:

    select distinct delta_value->0 as domain
    from (
      select
        json_array_elements(data.value::json->'new')::jsonb as delta_value
      from data
      union all
      select
        json_array_elements(data.value::json->'updated')::jsonb as delta_value
      from data
      union all
      select
        json_array_elements(data.value::json->'deleted')::jsonb as delta_value
      from data
    ) as delta_values
"""
import contextlib
import os

import redis


EXPIRY = 604800  # 7 days in seconds.


class RedisStatsStore(object):
    """The store for the statistics."""
    def __init__(self):
        self._conn = None
        self._url = os.getenv('REDIS_URL')

    @property
    def r_conn(self):
        """I am a redis connection!!!"""
        if self._conn is None:
            print 'new'
            self._conn = redis.from_url(self._url)
        return self._conn

    def note(self, domain):
        """Record that the domains have appeared in a delta report."""
        pipe = self.r_conn.pipeline()
        pipe.incr(domain)
        pipe.expire(domain, EXPIRY)
        pipe.execute()


if __name__ == '__main__':
    rs = RedisStatsStore()
    for i in range(10):
        rs.note('www.example.com')
