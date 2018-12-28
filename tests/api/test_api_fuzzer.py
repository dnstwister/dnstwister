"""The API's fuzzer endpoint."""
import binascii


def test_fuzzer(webapp):
    """Test the fuzzer."""
    domain = 'www.example.com'

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/fuzz/{}'.format(hexdomain)).json

    # Remove most of the results for the fuzzy domains
    response['fuzzy_domains'] = [response['fuzzy_domains'][0]]

    assert response == {
        u'domain': u'www.example.com',
        u'domain_as_hexadecimal': u'7777772e6578616d706c652e636f6d',
        u'fuzzy_domains': [{
            u'domain': u'www.example.com',
            u'domain_as_hexadecimal': u'7777772e6578616d706c652e636f6d',
            u'fuzz_url': u'http://localhost:80/api/fuzz/7777772e6578616d706c652e636f6d',
            u'fuzzer': u'Original*',
            u'parked_score_url': u'http://localhost:80/api/parked/7777772e6578616d706c652e636f6d',
            u'resolve_ip_url': u'http://localhost:80/api/ip/7777772e6578616d706c652e636f6d'
        }],
        u'parked_score_url': u'http://localhost:80/api/parked/7777772e6578616d706c652e636f6d',
        u'resolve_ip_url': u'http://localhost:80/api/ip/7777772e6578616d706c652e636f6d',
        u'url': u'http://localhost:80/api/fuzz/7777772e6578616d706c652e636f6d'
    }


def test_chunking_api_endpoint(webapp):
    """The new API endpoint uses chunked responses to handle long requests and
    to speed up page load times.
    """
    domain = 'a.com'
    hexdomain = binascii.hexlify(domain)
    response = webapp.get('/api/fuzz_chunked/{}'.format(hexdomain)).text

    assert response.startswith(
        u'{"ed": "612e636f6d", "d": "a.com"}\n\n{"ed": "61612e636f6d", "d": "aa.com"}\n\n'
    )
