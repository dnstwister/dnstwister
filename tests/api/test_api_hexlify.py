"""The API's hexlify endpoint."""
import binascii


def test_to_hex(webapp):
    """Test the hex helper."""
    domain = 'www.example.com'

    hexdomain = binascii.hexlify(domain)

    response = webapp.get('/api/to_hex/{}'.format(domain))

    assert response.json['domain_as_hexadecimal'] == hexdomain
