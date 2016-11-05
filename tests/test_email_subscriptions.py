"""Tests of the email subscription mechanism."""
import binascii
import flask
import mock
import pytest
import webtest.app

import dnstwister
import patches


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_bad_domains_fail(webapp):
    """Test the email views check domain validity."""
    with pytest.raises(webtest.app.AppError) as err:
        webapp.get('/email/subscribe/3234jskdnfsdf7y34')
    assert '400 BAD REQUEST' in err.value.message

    with pytest.raises(webtest.app.AppError) as err:
        webapp.post('/email/pending_verify/3234jskdnfsdf7y34')
    assert '400 BAD REQUEST' in err.value.message


def test_bad_error_codes(webapp):
    """Test the email error codes being weird doesn't break the page."""
    normal_html = webapp.get('/email/subscribe/www.example.com').html
    assert webapp.get('/email/subscribe/www.example.com/9').html == normal_html


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_verification_with_bad_id(webapp):
    """Test that verifying with a dud subscription id just redirects to root.
    """
    response = webapp.get('/email/verify/1234')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/'


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
def test_email_address_required():
    app = flask.ext.webtest.TestApp(dnstwister.app)

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)
    subscribe_path = '/email/subscribe/{}'.format(hexdomain)

    subscribe_page = app.get(subscribe_path)

    assert 'Email address is required' not in subscribe_page.body

    subscribe_page.form['email_address'] = ' '
    response = subscribe_page.form.submit()

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/email/subscribe/{}/0'.format(hexdomain)

    assert 'Email address is required' in response.follow().body


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

    sent_email = emailer.sent_emails[0][:2]

    assert sent_email == (
        'a@b.com', 'Please verify your subscription'
    )

    assert verify_url in emailer.sent_emails[0][2]

    subscribed_page = app.get(verify_path)

    assert 'You are now subscribed' in subscribed_page.body

    assert len(list(repository.isubscriptions())) == 1


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_unsubscribe():
    """Test can unsubscribe."""
    app = flask.ext.webtest.TestApp(dnstwister.app)
    repository = dnstwister.repository

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'

    assert len(list(repository.isubscriptions())) == 0

    repository.subscribe_email(sub_id, email, domain)

    assert len(list(repository.isubscriptions())) == 1

    app.get('/email/unsubscribe/{}'.format(sub_id))

    assert len(list(repository.isubscriptions())) == 0
