"""Test resolving IPs."""
import socket


def test_resolve(webapp):
    """Test we can resolve IP addresses."""
    response = webapp.get('/api/ip/646e73747769737465722e7265706f7274')

    assert response.status_code == 200

    payload = response.json
    ip_addr = payload['ip']
    del payload['ip']

    assert payload == {
        'domain': 'dnstwister.report',
        'domain_as_hexadecimal': '646e73747769737465722e7265706f7274',
        'error': False,
        'fuzz_url': 'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        'parked_score_url': 'http://localhost:80/api/parked/646e73747769737465722e7265706f7274',
        'url': 'http://localhost:80/api/ip/646e73747769737465722e7265706f7274'
    }

    # Will throw if invalid IP
    socket.inet_aton(ip_addr)


def test_failed_resolve(webapp):
    """Test basic failure to resolve an IP for a domain - because it's
    unregistered.
    """
    host = 'imprettysurethatthisdomaindoesnotexist.com'
    response = webapp.get('/api/ip/{}'.format(host))

    assert response.status_code == 200
    assert response.json['ip'] is False
    assert response.json['error'] is False
