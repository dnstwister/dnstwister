"""Whois integration test."""
import binascii


def test_whois_query(webapp):
    """Test the whois lookup."""
    domain = 'dnstwister.report'
    hexdomain = binascii.hexlify(domain)
    request = webapp.get('/api/whois/{}'.format(hexdomain))

    assert request.status_code == 200

    payload = request.json
    whois_text = payload['whois_text']

    del payload['whois_text']

    assert payload == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': hexdomain,
        u'fuzz_url': u'http://localhost/api/fuzz/{}'.format(hexdomain),
        u'parked_score_url': u'http://localhost/api/parked/{}'.format(hexdomain),
        u'resolve_ip_url': u'http://localhost/api/ip/{}'.format(hexdomain),
        u'url': u'http://localhost/api/whois/{}'.format(hexdomain),
    }

    assert 'Domain Name: dnstwister.report' in whois_text


def test_with_invalid_input(webapp):
    """Test with an invalid input."""
    domain = "foobar"

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/whois/{}'.format(hexdomain),
                          expect_errors=True).json

    error = response['error']
    assert error == 'Malformed domain or domain not represented in hexadecimal format.'
