"""Testing Unicode basics."""
# -*- coding: UTF-8 -*-
from dnstwister import dnstwist, tools


def test_decode_encoded_ascii_domain():
    assert tools.try_parse_domain_from_hex('7777772e6578616d706c652e636f6d') == 'www.example.com'


def test_decode_encoded_unicode_punycoded_domain():

    # www.xn--xampl-91ef.com in hex
    assert tools.try_parse_domain_from_hex('7777772e786e2d2d78616d706c2d393165662e636f6d') == u'www.\u0454xampl\u0454.com'


def test_idna_submit(webapp):
    """Can submit idna encoded."""
    idna_domain = 'xn--plnt-1na.com'  # 'plànt.com'

    response = webapp.post('/search', {'domains': idna_domain})

    assert response.headers['location'] == 'http://localhost/search?ed=786e2d2d706c6e742d316e612e636f6d'


def test_raw_unicode_submit(webapp):
    """Can submit idna encoded."""
    domain = u'pl\u00E0nt.com'  # 'plànt.com'

    response = webapp.post(
        '/search',
        {'domains': domain},
        content_type='application/x-www-form-urlencoded; charset=utf-8',
    )

    assert response.headers['location'] == 'http://localhost/search?ed=786e2d2d706c6e742d316e612e636f6d'
