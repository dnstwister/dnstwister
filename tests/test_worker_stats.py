'''Tests of the statistics worker.'''
import json

import mock

import dnstwister.workers.stats


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

    domains = when_the_worker_is_called()

    assert set(domains) == set(('mazon.com', 'amazont.com'))


def test_delta_domain_retriever_filters_invalid_domains(f_httpretty, monkeypatch):
    given_worker_will_retrieve_json(f_httpretty, monkeypatch, json.dumps({
        'values': [
            [None],
            ['??:SDmazon.com'],
            ['amazont.com'],
        ]
    }))

    domains = when_the_worker_is_called()

    assert set(domains) == set(('amazont.com',))


# Givens

def given_worker_will_retrieve_json(f_httpretty, monkeypatch, response_json):
    fake_url = 'http://127.0.0.1:9876/out.json'
    f_httpretty.register_uri(f_httpretty.GET, fake_url, body=response_json)
    monkeypatch.setenv('DELTAS_URL', fake_url)


# Whens

def when_the_worker_is_called():
    return dnstwister.workers.stats.get_delta_domains()
