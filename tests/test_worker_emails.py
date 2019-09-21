"""Tests the email worker."""
import datetime

import fakeredis
import mock

import dnstwister
import patches
import workers.email
import workers.deltas


def test_dont_send_when_no_changes(capsys, monkeypatch):
    """Test that emails are not sent when there are no changes."""

    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    # Return no IPs
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: (False, False)
    )
    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # We've not sent any emails as there were no changes (no IPs resolved at
    # all).
    assert len(emailer.sent_emails) == 0


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_dont_send_too_often(capsys, monkeypatch):
    """Test that emails are not sent more than every 24 hours."""

    # Patches
    monkeypatch.setenv('REDIS_URL', '')
    monkeypatch.setattr(
        'dnstwister.repository.db',
        patches.SimpleKVDatabase()
    )
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer',
        patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )
    emailer = patches.NoEmailer()
    monkeypatch.setattr(
        'workers.email.emailer',
        emailer
    )

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 1

    # Re-process immediately
    workers.email.process_sub(sub_id, sub_data)

    # Check we haven't sent two emails
    assert len(emailer.sent_emails) == 1


def test_subscription_email_timing(capsys, monkeypatch):
    """Test that email subscriptions and delta reporting are in sync.

    A bug was found where, because signing up registers for delta reporting
    and the email is sent as soon as the report is generated, it is possible
    to send 2 emails between delta reports.
    """

    # Patch away
    monkeypatch.setattr(
        'dnstwister.repository.db',
        patches.SimpleKVDatabase()
    )
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer',
        patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )
    emailer = patches.NoEmailer()
    monkeypatch.setattr(
        'workers.email.emailer',
        emailer
    )

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # We start with an unregistered domain.
    assert not repository.is_domain_registered(domain)

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Subscribing a user does not register the domain.
    assert not repository.is_domain_registered(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # We won't have sent any emails.
    assert emailer.sent_emails == []

    # But the domain is now registered for delta reporting.
    assert repository.is_domain_registered(domain)

    # So let's do a delta report.
    workers.deltas.process_domain(domain)
    delta_updated_time = datetime.datetime.now()

    # Process the subscription again.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 1

    # Now we "let" a bit over 24 hours pass since the email was sent and the
    # report was updated.
    passed_time = datetime.timedelta(hours=24, minutes=1)
    repository.update_last_email_sub_sent_date(
        sub_id,
        delta_updated_time,
        datetime.datetime.now() - passed_time
    )
    delta_report = repository.get_delta_report(domain)
    repository.update_delta_report(
        domain, delta_report, datetime.datetime.now() - passed_time
    )

    # Now we run the email worker for the sub *before* the delta report.
    workers.email.process_sub(sub_id, sub_data)

    # We've not sent an extra email because it's more than 23 hours since the
    # last delta report.
    assert len(emailer.sent_emails) == 1

    # As soon as the delta report is ran again we can send another email.
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.222', False)
    )
    workers.deltas.process_domain(domain)
    workers.email.process_sub(sub_id, sub_data)
    assert len(emailer.sent_emails) == 2

    # And the emails are different.
    assert emailer.sent_emails[0] != emailer.sent_emails[1]


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_dont_send_when_only_noisy(capsys, monkeypatch):
    """Test that emails are not sent when no non-noisy domains exist in
    delta report.
    """

    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    # Enable noisy domains functionality
    monkeypatch.setenv('feature.noisy_domains', 'true')

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Mark the found domain as also noisy.
    store = dnstwister.stats_store
    for _ in range(5):
        store.note('www.example.co')

    # Subscribe a new user, with noisy filtering enabled.
    repository.subscribe_email(sub_id, email, domain, True)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # We've not sent any emails as there were no changes (no IPs resolved at
    # all).
    assert len(emailer.sent_emails) == 0


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_send_when_only_noisy_but_noisy_feature_off(capsys, monkeypatch):
    """Test that emails are sent when no non-noisy domains exist in
    delta report, but the feature is disabled.
    """

    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Mark the found domain as also noisy.
    store = dnstwister.stats_store
    for _ in range(5):
        store.note('www.example.co')

    # Subscribe a new user, with noisy filtering enabled.
    repository.subscribe_email(sub_id, email, domain, True)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # We have an email.
    assert len(emailer.sent_emails) == 1

    # And there is no reference to noisy domains in the email.
    assert 'noisy' not in emailer.sent_emails[0][2]


@mock.patch('redis.from_url', fakeredis.FakeStrictRedis)
def test_pre_noisy_domain_subscriptions_default_to_off(capsys, monkeypatch):
    """Test that subscriptions prior to noisy domains existing are supported
    still but default to 'off'.
    """

    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Enable noisy domains functionality
    monkeypatch.setenv('feature.noisy_domains', 'true')

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Mark the found domain as also noisy.
    store = dnstwister.stats_store
    for _ in range(5):
        store.note('www.example.co')

    # Subscribe a new user, make them look like the pre-feature style.
    repository.subscribe_email(sub_id, email, domain, True)
    del(repository.db._data['email_sub:1234']['hide_noisy'])

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # We have an email.
    assert len(emailer.sent_emails) == 1

    # And there is no reference to noisy domains in the email.
    assert 'noisy' not in emailer.sent_emails[0][2]


def test_email_last_sent_has_delta_updated_datetime(capsys, monkeypatch):
    """Test that email_last_sent has a delta datetime included.
    """
    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Enable noisy domains functionality
    monkeypatch.setenv('feature.noisy_domains', 'true')

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 1

    # The last_sent field should have the delta updated datetime.
    last_sent_data = repository.db.data['email_sub_last_sent:{}'.format(sub_id)]

    when_date = repository.db.from_db_datetime(last_sent_data['when'])
    delta_date = repository.db.from_db_datetime(last_sent_data['delta_date'])

    assert isinstance(when_date, datetime.datetime)
    assert isinstance(delta_date, datetime.datetime)


def test_email_last_sent_is_backwards_compatible(capsys, monkeypatch):
    """Test that older email_last_sent fields are still compatible with the
    workers.
    """
    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Enable noisy domains functionality
    monkeypatch.setenv('feature.noisy_domains', 'true')

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 1

    # Now we can update the last_sent value to < 24 hours ago using the
    # old-style format old-style that was just a datetime field.
    past_date = datetime.datetime.now() - datetime.timedelta(hours=1)
    past_date_string = repository.db.to_db_datetime(past_date)
    repository.db.set('email_sub_last_sent', sub_id, past_date_string)

    # And we've not sent an email.
    assert len(emailer.sent_emails) == 1

    # Now we can update the last_sent value to > 24 hours ago to send another,
    # using the old-style format that was just a datetime field.
    past_date = datetime.datetime.now() - datetime.timedelta(hours=36)
    past_date_string = repository.db.to_db_datetime(past_date)
    repository.db.set('email_sub_last_sent', sub_id, past_date_string)

    # Process the subscription again.
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent another email.
    assert len(emailer.sent_emails) == 2


def test_email_worker_handles_updated_delta_without_date(capsys, monkeypatch):
    """Test of an edge case where one but not both keys is updated.
    """
    # Patches
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )

    # Enable noisy domains functionality
    monkeypatch.setenv('feature.noisy_domains', 'true')

    # Ensure the fake redis will work.
    monkeypatch.setenv('REDIS_URL', '')

    # Return a result
    monkeypatch.setattr(
        'dnstwister.tools.resolve',
        lambda domain: ('999.999.999.999', False)
    )

    emailer = patches.NoEmailer()
    monkeypatch.setattr('workers.email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Subscribe a new user.
    repository.subscribe_email(sub_id, email, domain, False)

    # Do a delta report.
    workers.deltas.process_domain(domain)

    # Don't set the updated date
    repository.db.delete('delta_report_updated', domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent no emails.
    assert len(emailer.sent_emails) == 0

    # Do a delta report properly this time.
    workers.deltas.process_domain(domain)

    # Process the subscription.
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    workers.email.process_sub(sub_id, sub_data)

    # And we've sent an email.
    assert len(emailer.sent_emails) == 0
