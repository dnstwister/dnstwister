"""Tests of the statistics worker.

Also first crack at using a Given-When-Then syntax, may change it if it sucks.
"""
import json

import fakeredis
import mock
import pytest

import dnstwister.storage.redis_stats_store
import dnstwister.workers.stats


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_new_domains_are_added_to_redis(f_httpretty, monkeypatch):
    given_an_empty_redis_database(monkeypatch)
    given_delta_domains(f_httpretty, monkeypatch, (
        'mazon.com', 'amazont.com'
    ))

    redis_state = when_the_worker_is_ran(monkeypatch)

    assert redis_state == [
        ('amazont.com', '1'),
        ('mazon.com', '1')
    ]


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_existing_domains_are_incremented(f_httpretty, monkeypatch):
    given_an_empty_redis_database(monkeypatch)
    given_delta_domains(f_httpretty, monkeypatch, (
        'mazon.com', 'amazont.com'
    ))

    when_the_worker_is_ran(monkeypatch)
    redis_state = when_the_worker_is_ran(monkeypatch)

    assert redis_state == [
        ('amazont.com', '2'),
        ('mazon.com', '2')
    ]


def test_delta_domain_retriever_returns_domains_list(f_httpretty, monkeypatch):
    given_worker_will_retrieve_json(f_httpretty, monkeypatch, json.dumps({
        'title': 'deltas datasource',
        'fields': ['domain'],
        'types': [25],
        'type_names': ['text'],
        'values': [
            ['mazon.com'],
            ['amazont.com'],
        ]
    }))

    domains = when_the_delta_domains_are_retrieved()

    assert set(domains) == set(('mazon.com', 'amazont.com'))


def test_delta_domain_retriever_requires_deltas_url(f_httpretty, monkeypatch):

    # No DELTAS_URL set by default.

    expected_message = 'Delta report URL configuration not set!'
    with pytest.raises(Exception, message=expected_message):
        when_the_delta_domains_are_retrieved()


def test_delta_domain_retriever_filters_invalid_domains(f_httpretty, monkeypatch):
    given_worker_will_retrieve_json(f_httpretty, monkeypatch, json.dumps({
        'values': [
            [None],
            ['??:SDmazon.com'],
            ['amazont.com'],
        ]
    }))

    domains = when_the_delta_domains_are_retrieved()

    assert set(domains) == set(('amazont.com',))


# Givens

def given_an_empty_redis_database(monkeypatch):
    monkeypatch.setenv('REDIS_URL', '')
    store = dnstwister.storage.redis_stats_store.RedisStatsStore()
    store.r_conn.flushall()


def given_delta_domains(f_httpretty, monkeypatch, domains):
    response_json = json.dumps({
        'values': [[domain] for domain in domains]
    })
    given_worker_will_retrieve_json(f_httpretty, monkeypatch, response_json)


def given_worker_will_retrieve_json(f_httpretty, monkeypatch, response_json):
    fake_url = 'http://127.0.0.1:9876/out.json'
    f_httpretty.register_uri(f_httpretty.GET, fake_url, body=response_json)
    monkeypatch.setenv('DELTAS_URL', fake_url)


# Whens

def when_the_worker_is_ran(monkeypatch):
    monkeypatch.setenv('REDIS_URL', '')
    dnstwister.workers.stats.main()

    store = dnstwister.storage.redis_stats_store.RedisStatsStore()
    return [(key, store.r_conn.get(key))
            for key
            in sorted(store.r_conn.keys())]


def when_the_delta_domains_are_retrieved():
    return dnstwister.workers.stats.get_delta_domains()
