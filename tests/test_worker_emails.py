"""Tests the email worker."""
import datetime

import dnstwister
import patches
import worker_email
import worker_deltas


def test_subscription_email_timing(capsys, monkeypatch):
    """Test that email subscriptions and delta reporting are in sync.

    A bug was found where a delta report was being done before subscription,
    causing two emails with the same data to be sent.
    """

    # Patch away
    monkeypatch.setattr('dnstwister.repository.db', patches.SimpleKVDatabase())
    monkeypatch.setattr(
        'dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer
    )
    monkeypatch.setattr(
        'dnstwister.tools.resolve', lambda domain: ('999.999.999.999', False)
    )
    emailer = patches.NoEmailer()
    monkeypatch.setattr('worker_email.emailer', emailer)

    repository = dnstwister.repository

    # Settings
    domain = 'www.example.com'
    sub_id = '1234'
    email = 'a@b.zzzzzzzzzzz'

    # Perform a delta report - for instance someone might have read an RSS
    # feed for the domain in the last 7 days.
    repository.register_domain(domain)
    worker_deltas.process_domain(domain)

    # Set the time to be a little while ago
    key = 'delta_report_updated:{}'.format(domain)
    updated = datetime.datetime.strptime(
        repository.db.data[key],
        '%Y-%m-%dT%H:%M:%SZ'
    )
    updated -= datetime.timedelta(hours=1)
    repository.db.data[key] = updated.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Subscribe a new user
    repository.subscribe_email(sub_id, email, domain)

    # Process the subscription
    sub_data = repository.db.data['email_sub:{}'.format(sub_id)]
    worker_email.process_sub(sub_id, sub_data)

    # We now have sent out an email
    sent_results = emailer.sent_emails[0][2]
