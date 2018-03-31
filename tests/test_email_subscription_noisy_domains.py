"""Tests of the per-sub noisy domain listing."""
import fakeredis
import mock

import dnstwister
import patches


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_invalid_sub_redirects_to_home(webapp):
    response = webapp.get('/email/234234234/noisy')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/'


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_no_fuzzy_domains_returns_notice(webapp, monkeypatch):
    monkeypatch.setenv('REDIS_URL', '')
    repository = dnstwister.repository

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'

    repository.subscribe_email(sub_id, email, domain, False)

    response = webapp.get('/email/1234/noisy')

    assert response.status_code == 200
    assert 'We\'ve not yet identified any "noisy" domains for' in response.body


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_fuzzy_domains_are_listed(webapp, monkeypatch):
    monkeypatch.setenv('REDIS_URL', '')
    monkeypatch.setenv('feature.noisy_domains', 'true')
    repository = dnstwister.repository

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'

    repository.subscribe_email(sub_id, email, domain, False)

    # Mark a domain as noisy.
    for _ in range(5):
        dnstwister.stats_store.note('www.exumple.com')

    response = webapp.get('/email/1234/noisy')

    assert response.status_code == 200
    assert 'www.exumple.com' in response.body
    assert '/analyse/7777772e6578756d706c652e636f6d' in response.body
    assert '/search/7777772e6578756d706c652e636f6d' in response.body
    assert '/email/subscribe/7777772e6578756d706c652e636f6d' in response.body
