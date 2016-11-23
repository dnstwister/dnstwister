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
        'domain': 'www.example.com',
        'domain_as_hexadecimal': '7777772e6578616d706c652e636f6d',
        'fuzzy_domains': [{
            'domain': 'www.example.com',
            'domain_as_hexadecimal': '7777772e6578616d706c652e636f6d',
            'fuzz_url': 'http://localhost:80/api/fuzz/7777772e6578616d706c652e636f6d',
            'fuzzer': 'Original*',
            'parked_score_url': 'http://localhost:80/api/parked/7777772e6578616d706c652e636f6d',
            'resolve_ip_url': 'http://localhost:80/api/ip/7777772e6578616d706c652e636f6d'
        }],
        'parked_score_url': 'http://localhost:80/api/parked/7777772e6578616d706c652e636f6d',
        'resolve_ip_url': 'http://localhost:80/api/ip/7777772e6578616d706c652e636f6d',
        'url': 'http://localhost:80/api/fuzz/7777772e6578616d706c652e636f6d'
    }
