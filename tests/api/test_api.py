"""The API's basic endpoint."""
import pytest
import webtest.app


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


def test_api_domain_validation(webapp):
    """Test that domains are validated on all API endpoints."""
    malformed_domain = 'example'
    endpoints = ('fuzz', 'to_hex', 'ip', 'parked', 'safebrowsing', 'whois')
    for endpoint in endpoints:
        with pytest.raises(webtest.app.AppError) as err:
            webapp.get('/api/{}/{}'.format(endpoint, malformed_domain))
        assert '400 BAD REQUEST' in err.value.message


def test_unicode_domain_passthrough(webapp):
    """Unicode is mean.

    I'm using: u'www.\u0454xampl\u0454.com'

    Which is xn--www.xampl.com-ehlf in punycode.
    """
    return

    malformed_domain = '786e2d2d7777772e78616d706c2e636f6d2d65686c66'
    endpoints = ('fuzz', 'to_hex', 'ip', 'parked', 'safebrowsing', 'whois')
    for endpoint in endpoints:
        with pytest.raises(webtest.app.AppError) as err:
            webapp.get('/api/{}/{}'.format(endpoint, malformed_domain))
        assert '400 BAD REQUEST' in err.value.message
