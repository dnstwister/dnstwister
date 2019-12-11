"""The API's hexlify endpoint."""
import binascii


def test_to_hex(webapp):
    """Test the hex helper."""
    domain = 'www.example.com'

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/to_hex/{}'.format(domain))

    assert response.json['domain_as_hexadecimal'] == hexdomain


def test_to_hex_with_invalid_input(webapp):
    """Test the hex helper with an invalid input."""
    domain = 'foobar'

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/to_hex/{}'.format(domain),
                          expect_errors=True).json

    error = response['error']
    assert error == 'Malformed domain.'
