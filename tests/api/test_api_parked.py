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
    assert response['redirects_to'] == ''


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

    assert response['score'] == 0.58
    assert response['score_text'] == 'Fairly likely'
    assert response['redirects']
    assert response['redirects_to'] == 'forsale.com'
