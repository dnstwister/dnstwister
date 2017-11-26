"""Tests of the noisy domain redis data."""
import fakeredis
import mock

import dnstwister.storage.redis_stats_store


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_not_noisy_under_threshold(f_httpretty, monkeypatch):
    given_an_empty_redis_database(monkeypatch)
    given_a_score_of(monkeypatch, 'www.example.com', 3)

    then_the_domain_noisy_state_is(monkeypatch, 'www.example.com', False)


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_is_noisy_over_threshold(f_httpretty, monkeypatch):
    given_an_empty_redis_database(monkeypatch)
    given_a_score_of(monkeypatch, 'www.example.com', 4)

    then_the_domain_noisy_state_is(monkeypatch, 'www.example.com', True)


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_not_noisy_if_not_exist_in_database_yet(f_httpretty, monkeypatch):
    given_an_empty_redis_database(monkeypatch)

    then_the_domain_noisy_state_is(monkeypatch, 'www.example.com', False)


# Givens

def given_an_empty_redis_database(monkeypatch):
    monkeypatch.setenv('REDIS_URL', '')
    store = dnstwister.storage.redis_stats_store.RedisStatsStore()
    store.r_conn.flushall()


def given_a_score_of(monkeypatch, domain, score):
    monkeypatch.setenv('REDIS_URL', '')
    store = dnstwister.storage.redis_stats_store.RedisStatsStore()
    for _ in range(score):
        store.note(domain)


# Thens

def then_the_domain_noisy_state_is(monkeypatch, domain, is_noisy):
    monkeypatch.setenv('REDIS_URL', '')
    store = dnstwister.storage.redis_stats_store.RedisStatsStore()
    assert store.is_noisy(domain) == is_noisy
