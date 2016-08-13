"""The API's basic endpoint."""


def test_api_root(webapp):
    """Test the API root."""
    assert webapp.get('/api/').json == {
        'domain_fuzzer_url': 'http://localhost:80/api/fuzz/{domain_as_hexadecimal}',
        'domain_to_hexadecimal_url': 'http://localhost:80/api/to_hex/{domain}',
        'ip_resolution_url': 'http://localhost:80/api/ip/{domain_as_hexadecimal}',
        'parked_check_url': 'http://localhost:80/api/parked/{domain_as_hexadecimal}',
        'google_safe_browsing_url': 'http://localhost:80/api/safebrowsing/{domain_as_hexadecimal}',
        'whois_url': 'http://localhost:80/api/whois/{domain_as_hexadecimal}',
        'url': 'http://localhost:80/api/',
    }


def test_api_root_redirect(webapp):
    """Test the /api -> /api/ redirect."""
    request = webapp.get('/api')

    assert request.status_code == 301
    assert request.headers['location'] == 'http://localhost/api/'
