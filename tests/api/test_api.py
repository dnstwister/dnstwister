"""The API's basic endpoint."""
import pytest
import webtest.app

from dnstwister import tools


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


def test_unicode_basics(webapp):
    """Test that Unicode domains work on all endpoints."""
    unicode_domain = 'xn--sterreich-z7a.icom.museum'.decode('idna')
    endpoints = ('fuzz', 'ip', 'parked', 'safebrowsing', 'whois')
    for endpoint in endpoints:
        webapp.get('/api/{}/{}'.format(
            endpoint,
            tools.encode_domain(unicode_domain),
        ))
    webapp.get('/api/to_hex/{}'.format(unicode_domain.encode('idna')))
