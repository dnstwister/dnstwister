"""Test of the storage implementation"""
import pytest

import dnstwister.storage.redis_stats_store


def test_stats_store_requires_redis_url(f_httpretty, monkeypatch):

    # No REDIS_URL set by default, but just in case it's currently in the
    # env...
    monkeypatch.delenv('REDIS_URL', raising=False)

    with pytest.raises(Exception) as ex:
        store = dnstwister.storage.redis_stats_store.RedisStatsStore()
        store.r_conn  # Enough to check for the URL

    assert ex.value.message == 'REDIS connection configuration not set!'
