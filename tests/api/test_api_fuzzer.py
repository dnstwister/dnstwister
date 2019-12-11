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
            u'fuzz_url': u'http://localhost/api/fuzz/7777772e6578616d706c652e636f6d',
            u'fuzzer': u'Original*',
            u'parked_score_url': u'http://localhost/api/parked/7777772e6578616d706c652e636f6d',
            u'resolve_ip_url': u'http://localhost/api/ip/7777772e6578616d706c652e636f6d'
        }],
        u'parked_score_url': u'http://localhost/api/parked/7777772e6578616d706c652e636f6d',
        u'resolve_ip_url': u'http://localhost/api/ip/7777772e6578616d706c652e636f6d',
        u'url': u'http://localhost/api/fuzz/7777772e6578616d706c652e636f6d'
    }


def test_fuzzer_with_invalid_input(webapp):
    """Test the fuzzer with an invalid input."""
    domain = "foobar"

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/fuzz/{}'.format(hexdomain),
                          expect_errors=True).json

    error = response['error']
    assert error == 'Malformed domain or domain not represented in hexadecimal format.'
