"""Test resolving IPs."""
import binascii
import socket


def test_resolve(webapp):
    """Test we can resolve IP addresses."""
    domain = 'dnstwister.report'
    hexdomain = binascii.hexlify(domain)
    response = webapp.get('/api/ip/{}'.format(hexdomain))

    assert response.status_code == 200

    payload = response.json
    ip_addr = payload['ip']
    del payload['ip']

    assert payload == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': hexdomain,
        u'error': False,
        u'fuzz_url': u'http://localhost:80/api/fuzz/{}'.format(hexdomain),
        u'parked_score_url': u'http://localhost:80/api/parked/{}'.format(hexdomain),
        u'url': u'http://localhost:80/api/ip/{}'.format(hexdomain),
    }

    # Will throw socket.error exception if this is not a valid IP address.
    socket.inet_aton(ip_addr)


def test_failed_resolve(webapp):
    """Test basic failure to resolve an IP for a domain - because it's
    unregistered.
    """
    domain = 'imprettysurethatthisdomaindoesnotexist.com'
    response = webapp.get('/api/ip/{}'.format(binascii.hexlify(domain)))

    assert response.status_code == 200
    assert response.json['ip'] is False
    assert response.json['error'] is False
