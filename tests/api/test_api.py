"""The API's basic endpoint."""
import binascii

import pytest
import webtest.app

from dnstwister import tools
from dnstwister.core.domain import Domain
from dnstwister.api.checks import shared


def test_api_root(webapp):
    """Test the API root."""
    assert webapp.get('/api/').json == {
        'domain_fuzzer_url': 'http://localhost/api/fuzz/{domain_as_hexadecimal}',
        'domain_to_hexadecimal_url': 'http://localhost/api/to_hex/{domain}',
        'ip_resolution_url': 'http://localhost/api/ip/{domain_as_hexadecimal}',
        'parked_check_url': 'http://localhost/api/parked/{domain_as_hexadecimal}',
        'google_safe_browsing_url': 'http://localhost/api/safebrowsing/{domain_as_hexadecimal}',
        'whois_url': 'http://localhost/api/whois/{domain_as_hexadecimal}',
        'url': 'http://localhost/api/',
    }


def test_api_root_redirect(webapp):
    """Test the /api -> /api/ redirect."""
    request = webapp.get('/api')

    assert request.status_code == 308
    assert request.headers['location'] == 'http://localhost/api/'


def test_api_domain_validation(webapp):
    """Test that domains are validated on all API endpoints."""
    malformed_domain = 'example'
    endpoints = ('fuzz', 'to_hex', 'ip', 'parked', 'safebrowsing', 'whois')
    for endpoint in endpoints:
        with pytest.raises(webtest.app.AppError) as err:
            webapp.get('/api/{}/{}'.format(
                endpoint,
                binascii.hexlify(malformed_domain.encode()).decode()
            ))
        assert '400 BAD REQUEST' in str(err)


def test_unicode_basics(webapp):
    """Test that Unicode domains work on all endpoints."""
    unicode_domain = Domain('xn--sterreich-z7a.icom.museum')
    endpoints = ('fuzz', 'ip', 'parked', 'safebrowsing', 'whois')
    for endpoint in endpoints:
        webapp.get('/api/{}/{}'.format(
            endpoint,
            unicode_domain.to_hex(),
        ))
    webapp.get('/api/to_hex/{}'.format(unicode_domain.to_ascii()))


def test_get_domain():
    assert shared.get_domain('https://example.com:443') == Domain('example.com')
    assert shared.get_domain('https://example.com') == Domain('example.com')
    assert shared.get_domain('http://example.com') == Domain('example.com')
