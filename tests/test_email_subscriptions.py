"""Tests of the email subscription mechanism."""
import binascii
import flask_webtest
import mock
import pytest
import webtest.app

import dnstwister
import dnstwister.tools
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
    normal_html = webapp.get('/email/subscribe/7777772e6578616d706c652e636f6d').html

    assert webapp.get(
        '/email/subscribe/7777772e6578616d706c652e636f6d/9',
        expect_errors=True
    ).html == normal_html


@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_verification_with_bad_id(webapp):
    """Test that verifying with a dud subscription id just redirects to root.
    """
    response = webapp.get('/email/verify/1234', expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/'


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

    repository.subscribe_email(sub_id, email, domain, False)

    subs = list(repository.isubscriptions())

    assert len(subs) == 1

    assert sorted(subs[0][1].keys()) == [
        'domain', 'email_address', 'hide_noisy'
    ]
    assert subs[0][1]['domain'] == domain
    assert subs[0][1]['email_address'] == email
    assert subs[0][1]['hide_noisy'] == False


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_email_address_required():
    app = flask_webtest.TestApp(dnstwister.app)

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)
    subscribe_path = '/email/subscribe/{}'.format(hexdomain)

    subscribe_page = app.get(subscribe_path)

    assert 'Email address is required' not in subscribe_page.body

    subscribe_page.form['email_address'] = ' '
    response = subscribe_page.form.submit()

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/email/subscribe/{}/0?hide_noisy=False'.format(hexdomain)

    assert 'Email address is required' in response.follow().body


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_email_address_validation_remembers_hide_noisy_flag():
    app = flask_webtest.TestApp(dnstwister.app)

    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)
    subscribe_path = '/email/subscribe/{}'.format(hexdomain)

    subscribe_page = app.get(subscribe_path)

    subscribe_page.form['email_address'] = ' '
    subscribe_page.form['hide_noisy'] = 'true'
    response = subscribe_page.form.submit()

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/email/subscribe/{}/0?hide_noisy=True'.format(hexdomain)

    assert 'Email address is required' in response.follow().body


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_link():
    app = flask_webtest.TestApp(dnstwister.app)
    emailer = dnstwister.views.www.email.emailer
    repository = dnstwister.repository

    assert emailer.sent_emails == []

    domain = 'a.com'
    hexdomain = dnstwister.tools.encode_domain(domain)
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
    verify_url = 'http://localhost{}'.format(verify_path)

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
    app = flask_webtest.TestApp(dnstwister.app)
    repository = dnstwister.repository

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'

    assert len(list(repository.isubscriptions())) == 0

    repository.subscribe_email(sub_id, email, domain, False)

    assert len(list(repository.isubscriptions())) == 1

    app.get('/email/unsubscribe/{}'.format(sub_id))

    assert len(list(repository.isubscriptions())) == 0



@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_isubscriptions_link_unicode():
    app = flask_webtest.TestApp(dnstwister.app)
    emailer = dnstwister.views.www.email.emailer
    repository = dnstwister.repository

    assert emailer.sent_emails == []

    domain = u'\u0454a.com'  # ea.com, but with a funny 'e'
    hexdomain = dnstwister.tools.encode_domain(domain)
    subscribe_path = '/email/subscribe/{}'.format(hexdomain)

    search_page = app.get('/search/{}'.format(hexdomain))

    assert subscribe_path in search_page.body

    subscribe_page = app.get(subscribe_path)

    assert '\xd1\x94a.com (xn--a-9ub.com)' in subscribe_page.body

    subscribe_page.form['email_address'] = 'a@b.com'
    pending_page = subscribe_page.form.submit()

    assert pending_page.request.url.endswith('pending_verify/786e2d2d612d3975622e636f6d')
    assert '\xd1\x94a.com (xn--a-9ub.com)' in pending_page.body

    assert list(repository.isubscriptions()) == []

    verify_code = repository.db.data.items()[0][0].split(
        'email_sub_pending:'
    )[1]
    verify_path = '/email/verify/{}'.format(
        verify_code
    )
    verify_url = 'http://localhost{}'.format(verify_path)

    assert len(emailer.sent_emails) == 1

    sent_email = emailer.sent_emails[0][:2]

    assert sent_email == (
        'a@b.com', 'Please verify your subscription'
    )

    assert verify_url in emailer.sent_emails[0][2]

    subscribed_page = app.get(verify_path)

    assert 'You are now subscribed' in subscribed_page.body
    assert '\xd1\x94a.com (xn--a-9ub.com)' in subscribed_page.body

    assert len(list(repository.isubscriptions())) == 1


@mock.patch('dnstwister.views.www.email.emailer', patches.NoEmailer())
@mock.patch('dnstwister.repository.db', patches.SimpleKVDatabase())
def test_unsubscribe_unicode():
    """Test can unsubscribe."""
    app = flask_webtest.TestApp(dnstwister.app)
    repository = dnstwister.repository

    domain = u'www.\u0454xample.com'
    email = 'a@b.com'
    sub_id = '1234'

    assert len(list(repository.isubscriptions())) == 0

    repository.subscribe_email(sub_id, email, domain, False)

    assert len(list(repository.isubscriptions())) == 1

    app.get('/email/unsubscribe/{}'.format(sub_id))

    assert len(list(repository.isubscriptions())) == 0
