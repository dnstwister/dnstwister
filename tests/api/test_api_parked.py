"""The API's parked checker endpoint."""
import dnstwister.api.checks.parked as parked_api
from dnstwister.core.domain import Domain


def test_not_parked(f_httpretty, webapp):
    """Test when the domains don't redirect."""
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://www.example.com:80/',
        body=lambda request, uri, headers: (200, {}, 'OK'),
    )
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://www.example.com:80/dnstwister_parked_check',
        body=lambda request, uri, headers: (200, {}, 'OK'),
    )

    domain = 'www.example.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.0
    assert response['score_text'] == 'Unlikely'
    assert not response['redirects']
    assert response['redirects_to'] is None


def test_parked(f_httpretty, webapp):
    """Test when the domains don't redirect."""
    f_httpretty.register_uri(
        f_httpretty.GET,
        'http://www.example.com:80/',
        status=302,
        adding_headers={
            'location': 'http://forsale.com',
        }
    )

    f_httpretty.register_uri(
        f_httpretty.GET,
        'http://www.example.com:80/dnstwister_parked_check',
        status=302,
        adding_headers={
            'location': 'http://forsale.com',
        }
    )

    f_httpretty.register_uri(
        f_httpretty.GET,
        'http://forsale.com',
        body='Buy this domain right now!'
    )

    domain = 'www.example.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.64
    assert response['score_text'] == 'Quite likely'
    assert response['redirects']
    assert response['redirects_to'] == 'forsale.com'


def test_dressed_redirect(f_httpretty, webapp):
    """Test that going from naked to non-naked domain is not considered
    being parked.

    AKA, "dressing" the domain :)
    """
    f_httpretty.register_uri(
        f_httpretty.GET,
        'http://example.com:80/',
        status=302,
        adding_headers={
            'location': 'http://ww2.example.com',
        }
    )
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://example.com/dnstwister_parked_check',
        body=lambda request, uri, headers: (404, {}, 'Boom'),
    )
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://ww2.example.com',
        body=lambda request, uri, headers: (200, {}, 'OK'),
    )

    domain = 'example.com'
    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.0


def test_second_level_extraction():
    """Test we can extract second-level domains from tlds."""
    assert parked_api.second_level(Domain('www.example.com')) == 'example'
    assert parked_api.second_level(Domain('example.com')) == 'example'
    assert parked_api.second_level(Domain('www2.example.co.uk')) == 'example'


def test_dressed_check():
    """Tests the detail of the "dressed" detection."""
    assert parked_api.dressed(Domain('example.com'), Domain('www.example.com'))
    assert parked_api.dressed(Domain('example.com'), Domain('ww2.example.com'))
    assert parked_api.dressed(Domain('www.example.com'), Domain('example.com'))
    assert parked_api.dressed(Domain('www.example.com'), Domain('example.com.au'))

    assert not parked_api.dressed(Domain('www.example.com'), Domain('www.examples.com'))
