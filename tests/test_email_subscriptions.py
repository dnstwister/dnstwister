"""Tests of the email subscription mechanism."""
import binascii
import flask.ext.webtest
import mock

import dnstwister
import patches


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_with_no_subscriptions():
    repository = dnstwister.repository
    assert list(repository.isubscriptions()) == []


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_during_subscription():
    repository = dnstwister.repository

    email = 'a@b.com'
    verify_code = '1234'

    repository.stage_email_subscription(email, verify_code)

    assert list(repository.isubscriptions()) == []

    assert list(repository.isubscriptions(list_all=True)) != []

    repository.subscribe_email(verify_code, 'www.example.com')

    subs = list(repository.isubscriptions())

    assert len(subs) == 1

    assert sorted(subs[0][1].keys()) == [
        'created', 'domain', 'email', 'last_sent'
    ]
    assert subs[0][1]['domain'] == 'www.example.com'
    assert subs[0][1]['email'] == 'a@b.com'
    assert subs[0][1]['last_sent'] is None


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_link():
    app = flask.ext.webtest.TestApp(dnstwister.app)
    emailer = dnstwister.views.www.email.emailer
    repository = dnstwister.repository

    assert emailer.sent_emails == []

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)
    subscribe_path = '/email/subscribe/{}'.format(hexdomain)

    search_page = app.get('/search/{}'.format(hexdomain))

    assert subscribe_path in search_page.body

    subscribe_page = app.get(subscribe_path)

    subscribe_page.form['email'] = 'a@b.com'
    subscribe_page.form.submit()

    assert list(repository.isubscriptions()) == []

    staged_subscription = list(repository.isubscriptions(list_all=True))[0]
    verify_code = staged_subscription[0]
    verify_path = '/email/verify/{}/{}'.format(
        hexdomain, verify_code
    )
    verify_url = 'http://localhost:80{}'.format(verify_path)

    assert len(emailer.sent_emails) == 1

    sent_email = emailer.sent_emails[0]

    assert sent_email == (
        'a@b.com', 'Please verify your subscription', verify_url
    )

    subscribed_page = app.get(verify_path)

    assert 'You are now subscribed' in subscribed_page.body

    assert len(list(repository.isubscriptions())) == 1

    # Check cannot overwrite an existing verification with a new domain.
    verify_path = '/email/verify/{}/{}'.format(
        binascii.hexlify('b.com'), verify_code
    )
    app.get(verify_path)

    assert len(list(repository.isubscriptions())) == 1
    assert repository.isubscriptions().next()[1]['domain'] == 'a.com'
