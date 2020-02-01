"""Test resolving IPs."""
import socket

from dnstwister import tools
from dnstwister.core.domain import Domain


def test_resolve(webapp):
    """Test we can resolve IP addresses."""
    domain = 'dnstwister.report'
    hexdomain = Domain(domain).to_hex()
    response = webapp.get('/api/ip/{}'.format(hexdomain))

    assert response.status_code == 200

    payload = response.json
    ip_addr = payload['ip']
    del payload['ip']

    assert payload == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': hexdomain,
        u'error': False,
        u'fuzz_url': u'http://localhost/api/fuzz/{}'.format(hexdomain),
        u'parked_score_url': u'http://localhost/api/parked/{}'.format(hexdomain),
        u'url': u'http://localhost/api/ip/{}'.format(hexdomain),
    }

    # Will throw socket.error exception if this is not a valid IP address.
    socket.inet_aton(ip_addr)


def test_unicode_resolve(webapp):
    """Check we can resolve a unicode domain.
    """
    domain = 'xn--sterreich-z7a.icom.museum'
    hexdomain = Domain(domain).to_hex()
    response = webapp.get('/api/ip/{}'.format(hexdomain))

    assert response.status_code == 200

    payload = response.json
    ip_addr = payload['ip']
    del payload['ip']

    assert payload == {
        u'domain': u'xn--sterreich-z7a.icom.museum',
        u'domain_as_hexadecimal': u'786e2d2d7374657272656963682d7a37612e69636f6d2e6d757365756d',
        u'error': False,
        u'fuzz_url': u'http://localhost/api/fuzz/786e2d2d7374657272656963682d7a37612e69636f6d2e6d757365756d',
        u'parked_score_url': u'http://localhost/api/parked/786e2d2d7374657272656963682d7a37612e69636f6d2e6d757365756d',
        u'url': u'http://localhost/api/ip/786e2d2d7374657272656963682d7a37612e69636f6d2e6d757365756d'
    }

    # Will throw socket.error exception if this is not a valid IP address.
    socket.inet_aton(ip_addr)


def test_failed_resolve(webapp):
    """Test basic failure to resolve an IP for a domain - because it's
    unregistered.
    """
    domain = 'imprettysurethatthisdomaindoesnotexist.com'
    response = webapp.get('/api/ip/{}'.format(Domain(domain).to_hex()))

    assert response.status_code == 200
    assert response.json['ip'] is False
    assert response.json['error'] is False
