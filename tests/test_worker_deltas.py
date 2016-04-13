"""Tests of the deltas worker."""
import datetime

import dnstwister
import patches
import worker_deltas


def test_invalid_domain_is_unregistered(capsys, monkeypatch):
    """Invalid domains are tidied up."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    repository = dnstwister.repository

    invalid_domain = '3j88??ASd'

    assert not repository.is_domain_registered(invalid_domain)

    repository.register_domain(invalid_domain)
    assert repository.is_domain_registered(invalid_domain)

    worker_deltas.process_domain(invalid_domain)
    assert not repository.is_domain_registered(invalid_domain)

    expected_output = 'Unregistering (invalid) {}\n'.format(invalid_domain)
    assert capsys.readouterr()[0] == expected_output


def test_new_domain_is_marked_as_read(capsys, monkeypatch):
    """New domain is marked as read at first pass."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    repository = dnstwister.repository

    domain = 'www.example.com'

    assert repository.delta_report_updated(domain) is None

    worker_deltas.process_domain(domain)

    assert repository.delta_report_updated(domain) is not None


def test_old_domain_is_unregistered(capsys, monkeypatch):
    """Long-time unread domains are unregistered."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    repository = dnstwister.repository

    domain = 'www.example.com'
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)

    assert repository.delta_report_last_read(domain) is None

    repository.mark_delta_report_as_read(domain, old_date)
    assert repository.delta_report_last_read(domain) == old_date.replace(
        microsecond=0
    )

    worker_deltas.process_domain(domain)
    assert repository.delta_report_last_read(domain) is None

    expected_output = 'Unregistering (not read > 7 days) {}\n'.format(domain)
    assert capsys.readouterr()[0] == expected_output
