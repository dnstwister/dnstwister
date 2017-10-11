"""Testing Unicode."""
import binascii

import dnstwister.tools as tools


def test_encode_ascii_domain():
    assert tools.encode_domain('www.example.com') == '7777772e6578616d706c652e636f6d'


def test_encode_unicode_domain():
    unicode_domain = u'www.\u0454xampl\u0454.com'
    punycode_domain = unicode_domain.encode('punycode')

    assert punycode_domain == 'www.xampl.com-ehlf'
    assert binascii.hexlify(punycode_domain) == '7777772e78616d706c2e636f6d2d65686c66'

    assert tools.encode_domain(unicode_domain) == '7777772e78616d706c2e636f6d2d65686c66'


def test_encode_punycoded_domain():
    punycode_domain = 'www.xampl.com-ehlf'

    assert tools.encode_domain(punycode_domain) == '7777772e78616d706c2e636f6d2d65686c66'


def test_decode_encoded_ascii_domain():
    assert tools.decode_domain('7777772e6578616d706c652e636f6d') == 'www.example.com'


def test_decode_encoded_unicode_or_punycoded_domain():
    assert tools.decode_domain('7777772e78616d706c2e636f6d2d65686c66') == u'www.\u0454xampl\u0454.com'
