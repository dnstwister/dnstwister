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
        u'fuzz_url': u'http://localhost:80/api/fuzz/{}'.format(hexdomain),
        u'parked_score_url': u'http://localhost:80/api/parked/{}'.format(hexdomain),
        u'resolve_ip_url': u'http://localhost:80/api/ip/{}'.format(hexdomain),
        u'url': u'http://localhost:80/api/whois/{}'.format(hexdomain),
    }

    assert 'Domain Name: dnstwister.report' in whois_text
