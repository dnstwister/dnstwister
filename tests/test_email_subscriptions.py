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

    domain = 'www.example.com'
    email = 'a@b.com'
    sub_id = '1234'
    payment_cust_id = 'cus_0000'

    repository.subscribe_email(sub_id, email, domain, payment_cust_id)

    subs = list(repository.isubscriptions())

    assert len(subs) == 1

    assert sorted(subs[0][1].keys()) == [
        'domain', 'email', 'last_sent', 'payment_customer_id'
    ]
    assert subs[0][1]['domain'] == domain
    assert subs[0][1]['email'] == email
    assert subs[0][1]['payment_customer_id'] == payment_cust_id
    assert subs[0][1]['last_sent'] is None
