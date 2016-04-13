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
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = 'www.example.com'

    assert repository.delta_report_updated(domain) is None

    worker_deltas.process_domain(domain)
    assert repository.delta_report_updated(domain) is not None
    assert capsys.readouterr()[0] != ''


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


def test_all_changes_are_new_on_first_delta(capsys, monkeypatch):
    """The first delta marks all resolved domains as 'new'."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = 'www.example.com'

    worker_deltas.process_domain(domain)
    assert capsys.readouterr()[0] != ''

    resolution_report = repository.get_resolution_report(domain)
    assert resolution_report == {
        'www.example.co': {'ip': '999.999.999.999', 'tweak': 'Pretend'}
    }

    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [],
        'new': [('www.example.co', '999.999.999.999')],
        'updated': []
    }


def test_updated_ip_is_noted_in_delta(capsys, monkeypatch):
    """IP updates are marked as 'updated'."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = 'www.example.com'

    worker_deltas.process_domain(domain)

    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('000.999.999.999', False)
    )

    # Mark the entry as 'old' to ensure it is re-run
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)
    db_key = 'delta_report_updated:{}'.format(domain)
    repository.db._data[db_key] = old_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    worker_deltas.process_domain(domain)
    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [],
        'updated': [('www.example.co', '999.999.999.999', '000.999.999.999')],
        'new': []
    }


def test_deleted_domain_is_noted_in_delta(capsys, monkeypatch):
    """Domain un-registrations are marked as 'deleted'."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = 'www.example.com'

    worker_deltas.process_domain(domain)

    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: (False, False)
    )

    # Mark the entry as 'old' to ensure it is re-run
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)
    db_key = 'delta_report_updated:{}'.format(domain)
    repository.db._data[db_key] = old_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    worker_deltas.process_domain(domain)
    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [('www.example.co')],
        'updated': [],
        'new': []
    }
