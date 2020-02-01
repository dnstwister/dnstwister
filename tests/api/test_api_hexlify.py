"""The API's hexlify endpoint."""
import binascii

from dnstwister.core.domain import Domain


def test_to_hex(webapp):
    """Test the hex helper."""
    domain = 'www.example.com'

    hexdomain = Domain(domain).to_hex()

    response = webapp.get('/api/to_hex/{}'.format(domain))

    assert response.json['domain_as_hexadecimal'] == hexdomain
