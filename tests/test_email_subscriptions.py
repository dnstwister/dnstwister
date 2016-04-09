"""Tests of the email subscription mechanism."""
import flask
import mock
import pytest
import webtest

import binascii
import dnstwister
import patches


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_with_no_subscriptions():
    repository = dnstwister.repository
    assert list(repository.isubscriptions()) == []


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_during_subscription():
    repository = dnstwister.repository

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'
    payment_cust_id = 'cus_0000'

    repository.subscribe_email(sub_id, email, domain)

    subs = list(repository.isubscriptions())

    assert len(subs) == 1

    assert sorted(subs[0][1].keys()) == [
        'domain', 'email_address'
    ]
    assert subs[0][1]['domain'] == domain
    assert subs[0][1]['email_address'] == email


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

    subscribe_page.form['email_address'] = 'a@b.com'
    subscribe_page.form.submit()

    assert list(repository.isubscriptions()) == []

    verify_code = repository.db.data.items()[0][0].split(
        'email_sub_pending:'
    )[1]
    verify_path = '/email/verify/{}'.format(
        verify_code
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
    verify_path = '/email/verify/{}'.format(
        binascii.hexlify('b.com'), verify_code
    )
    with pytest.raises(webtest.app.AppError):
        app.get(verify_path)

    assert len(list(repository.isubscriptions())) == 1
    assert repository.isubscriptions().next()[1]['domain'] == 'a.com'
