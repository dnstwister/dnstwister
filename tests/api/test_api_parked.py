"""The API's parked checker endpoint."""
import binascii


def test_not_parked(f_httpretty, webapp):
    """Test when the domains don't redirect."""

    f_httpretty.HTTPretty.allow_net_connect = False
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://www.example.com:80/',
        body=lambda request, uri, headers: (200, {}, 'OK'),
    )
    f_httpretty.register_uri(
        f_httpretty.GET, 'http://www.example.com:80/dnstwister_parked_check',
        body=lambda request, uri, headers: (200, {}, 'OK'),
    )

    domain = 'www.example.com'
    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.0
    assert response['score_text'] == 'Unlikely'
    assert not response['redirects']
    assert response['redirects_to'] is None


def test_parked(f_httpretty, webapp):
    """Test when the domains don't redirect."""

    f_httpretty.HTTPretty.allow_net_connect = False
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
    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.64
    assert response['score_text'] == 'Quite likely'
    assert response['redirects']
    assert response['redirects_to'] == 'forsale.com'


def test_dressed_redirect(f_httpretty, webapp):
    """Test that going from naked to non-naked domain is less of an issue.

    AKA, "dressing" the domain :)
    """

    f_httpretty.HTTPretty.allow_net_connect = False
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
    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/parked/{}'.format(hexdomain)).json

    assert response['score'] == 0.04
