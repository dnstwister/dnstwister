"""Parked check integration test."""
from dnstwister.core.domain import Domain


def test_parked_query(webapp):
    """Test the parked API against our own domain."""
    domain = 'dnstwister.report'
    hexdomain = Domain(domain).to_hex()
    request = webapp.get('/api/parked/{}'.format(hexdomain))

    assert request.status_code == 200

    assert request.json == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': hexdomain,
        u'dressed': False,
        u'fuzz_url': u'http://localhost/api/fuzz/{}'.format(hexdomain),
        u'redirects': False,
        u'redirects_to': None,
        u'resolve_ip_url': u'http://localhost/api/ip/{}'.format(hexdomain),
        u'score': 0.07,
        u'score_text': u'Possibly',
        u'url': u'http://localhost/api/parked/{}'.format(hexdomain),
    }


def test_parked_query_on_broken_domain(webapp):
    """Test the parked API against a domain that doesn't exist."""
    domain = 'there-is-little-chance-this-domain-exists-i-hope.com'
    hexdomain = Domain(domain).to_hex()
    request = webapp.get('/api/parked/{}'.format(hexdomain))

    assert request.status_code == 200
    assert request.json['score'] == 0
    assert request.json['redirects'] is False
    assert request.json['redirects_to'] is None
    assert request.json['score_text'] == 'Unlikely'
    assert request.json['dressed'] is False
