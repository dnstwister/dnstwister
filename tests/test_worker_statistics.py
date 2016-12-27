"""Tests of the statistics worker."""
import datetime

import dnstwister
import patches
import workers.statistics


def set_up_mocks(monkeypatch):
    mock_db = patches.SimpleKVDatabase()
    monkeypatch.setattr('dnstwister.repository.statistics.db', mock_db)
    monkeypatch.setattr('dnstwister.repository.db', mock_db)

    data_repository = dnstwister.repository
    statistics_repository = dnstwister.repository.statistics

    return data_repository, statistics_repository


def test_new_email_sub_creates_new_statistics(capsys, monkeypatch):
    """A new email sub will create a new set of statistics."""
    data_repository, statistics_repository = set_up_mocks(monkeypatch)

    # GIVEN a subscribed user with a delta report created.
    data_repository.subscribe_email('1234', 'a@b.com', 'example.com')
    data_repository.update_delta_report('example.com', {
        'new': [['exxample.com', '127.0.0.1']],
        'updated': [],
        'deleted': [],
    })

    # WHEN the email work is ran
    workers.statistics.increment_email_sub_deltas()

    # THEN statistics will be created for exxample.com.
    stats_data = statistics_repository.get_noise_stat('exxample.com')
    assert stats_data.domain == 'exxample.com'
    assert stats_data.deltas == 1


def test_statistics_worker_handles_no_delta_report(capsys, monkeypatch):
    """No delta report just means no statistics are generated."""
    data_repository, statistics_repository = set_up_mocks(monkeypatch)

    # GIVEN a subscribed user (and no delta report created).
    data_repository.subscribe_email('1234', 'a@b.com', 'example.com')

    # WHEN the email work is ran
    workers.statistics.increment_email_sub_deltas()

    # THEN nothing happens.
    assert statistics_repository.get_noise_stat('exxample.com') is None


def test_statistics_dont_update_in_under_a_day(capsys, monkeypatch):
    """Statistics will not update more than once a day."""
    data_repository, statistics_repository = set_up_mocks(monkeypatch)

    # GIVEN a subscribed user with a delta report created.
    data_repository.subscribe_email('1234', 'a@b.com', 'example.com')
    data_repository.update_delta_report('example.com', {
        'new': [['exxample.com', '127.0.0.1']],
        'updated': [],
        'deleted': [],
    })

    # GIVEN the statistic was checked within one day.
    now = datetime.datetime.now() - datetime.timedelta(hours=23)
    statistics_repository.mark_noise_stat_as_updated('exxample.com', now=now)

    # WHEN the email work is ran
    workers.statistics.increment_email_sub_deltas()

    # THEN no statistics will be created for exxample.com, even though there
    # is (now) a delta report.
    assert statistics_repository.get_noise_stat('exxample.com') is None


def test_statistics_dont_update_once_a_day(capsys, monkeypatch):
    """Statistics will only update once a day."""
    data_repository, statistics_repository = set_up_mocks(monkeypatch)

    # GIVEN a subscribed user with a delta report created.
    data_repository.subscribe_email('1234', 'a@b.com', 'example.com')
    data_repository.update_delta_report('example.com', {
        'new': [['exxample.com', '127.0.0.1']],
        'updated': [],
        'deleted': [],
    })

    # GIVEN the statistic was checked within one day.
    now = datetime.datetime.now() - datetime.timedelta(hours=24, minutes=1)
    statistics_repository.mark_noise_stat_as_updated('exxample.com', now=now)

    # WHEN the email work is ran
    workers.statistics.increment_email_sub_deltas()

    # THEN no statistics will be created for exxample.com, even though there
    # is (now) a delta report.
    # THEN statistics will be created for exxample.com.
    stats_data = statistics_repository.get_noise_stat('exxample.com')
    assert stats_data.domain == 'exxample.com'
    assert stats_data.deltas == 1
