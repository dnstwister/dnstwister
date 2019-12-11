"""Google Safebrowsing integration test."""
import binascii


def test_safebrowsing_query(webapp):
    """Test our domain is safe."""
    domain = 'dnstwister.report'
    hexdomain = binascii.hexlify(domain)
    response = webapp.get('/api/safebrowsing/{}'.format(hexdomain))

    assert response.status_code == 200

    assert response.json == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': hexdomain,
        u'fuzz_url': u'http://localhost/api/fuzz/{}'.format(hexdomain),
        u'issue_detected': False,
        u'parked_score_url': u'http://localhost/api/parked/{}'.format(hexdomain),
        u'resolve_ip_url': u'http://localhost/api/ip/{}'.format(hexdomain),
        u'url': u'http://localhost/api/safebrowsing/{}'.format(hexdomain),
    }


def test_safebrowsing_with_bad_domain(webapp):
    """Test against the google test domain (malware.testing.google.test)."""
    domain = 'malware.testing.google.test'
    hexdomain = binascii.hexlify(domain)
    response = webapp.get('/api/safebrowsing/{}'.format(hexdomain))

    assert response.status_code == 200
    assert response.json['issue_detected'] is True


def test_with_invalid_input(webapp):
    """Test with an invalid input."""
    domain = "foobar"

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/safebrowsing/{}'.format(hexdomain),
                          expect_errors=True).json

    error = response['error']
    assert error == 'Malformed domain or domain not represented in hexadecimal format.'
