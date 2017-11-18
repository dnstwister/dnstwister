"""Tests of the deltas worker."""
import datetime
import time

import dnstwister
import patches
import workers.deltas


def test_invalid_domain_is_unregistered(capsys, monkeypatch):
    """Invalid domains are tidied up."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    repository = dnstwister.repository

    invalid_domain = '3j88??ASd'

    assert not repository.is_domain_registered(invalid_domain)

    repository.register_domain(invalid_domain)
    assert repository.is_domain_registered(invalid_domain)

    workers.deltas.process_domain(invalid_domain)
    assert not repository.is_domain_registered(invalid_domain)

    expected_output = 'Unregistering (invalid) {}\n'.format(
        invalid_domain.encode('idna')
    )
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

    domain = u'www.\u0454xample.com'

    assert repository.delta_report_updated(domain) is None

    workers.deltas.process_domain(domain)
    assert repository.delta_report_updated(domain) is not None
    assert capsys.readouterr()[0] != ''


def test_old_domain_is_unregistered(capsys, monkeypatch):
    """Long-time unread domains are unregistered."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    repository = dnstwister.repository

    domain = u'www.\u0454xample.com'
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)

    assert repository.delta_report_last_read(domain) is None

    repository.mark_delta_report_as_read(domain, old_date)
    assert repository.delta_report_last_read(domain) == old_date.replace(
        microsecond=0
    )

    workers.deltas.process_domain(domain)
    assert repository.delta_report_last_read(domain) is None

    expected_output = 'Unregistering (not read > 7 days) {}\n'.format(
        domain.encode('idna')
    )
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

    domain = u'www.\u0454xample.com'

    workers.deltas.process_domain(domain)
    assert capsys.readouterr()[0] != ''

    resolution_report = repository.get_resolution_report(domain)
    assert resolution_report == {
        u'www.\u0454xample.co': {'ip': '999.999.999.999', 'tweak': 'Pretend'}
    }

    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [],
        'new': [(u'www.\u0454xample.co', '999.999.999.999')],
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

    domain = u'www.\u0454xample.com'

    workers.deltas.process_domain(domain)

    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('000.999.999.999', False)
    )

    # Mark the entry as 'old' to ensure it is re-run
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)
    db_key = u'delta_report_updated:{}'.format(domain)
    repository.db._data[db_key] = old_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    workers.deltas.process_domain(domain)
    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [],
        'updated': [(u'www.\u0454xample.co', '999.999.999.999', '000.999.999.999')],
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

    domain = u'www.\u0454xample.com'

    workers.deltas.process_domain(domain)

    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: (False, False)
    )

    # Mark the entry as 'old' to ensure it is re-run
    old_date = datetime.datetime.now() - datetime.timedelta(days=10)
    db_key = u'delta_report_updated:{}'.format(domain)
    repository.db._data[db_key] = old_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    workers.deltas.process_domain(domain)
    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [(u'www.\u0454xample.co')],
        'updated': [],
        'new': []
    }


def test_old_style_resolution_reports_are_updated(capsys, monkeypatch):
    """Test the migration to the more feature-rich reports works."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = u'www.\u0454xample.com'

    # Pre-load an old-style resolution report
    db_key = u'resolution_report:{}'.format(domain)
    repository.db._data[db_key] = {u'www.\u0454xample.co': '127.0.0.1'}

    workers.deltas.process_domain(domain)

    delta_report = repository.get_delta_report(domain)
    assert delta_report == {
        'deleted': [],
        'updated': [(u'www.\u0454xample.co', '127.0.0.1', '999.999.999.999')],
        'new': []
    }


def test_domains_are_checked_once_a_day(capsys, monkeypatch):
    """Test domains are not checked constantly."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    repository = dnstwister.repository

    domain = u'www.\u0454xample.com'

    workers.deltas.process_domain(domain)

    last_updated_db_key = u'delta_report_updated:{}'.format(domain)
    last_updated = repository.db._data[last_updated_db_key]

    # Process again not long after.
    time.sleep(2)
    workers.deltas.process_domain(domain)

    # Ensure that we didn't updated the last-updated date
    assert repository.db._data[last_updated_db_key] == last_updated


def test_domains_iter_lists_all_domains(capsys, monkeypatch):
    """Test the repo can return all domains registered."""
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    domain = u'www.\u0454xample.com'

    repository = dnstwister.repository

    assert list(repository.iregistered_domains()) == []

    repository.register_domain(domain)

    assert list(repository.iregistered_domains()) == [domain]
