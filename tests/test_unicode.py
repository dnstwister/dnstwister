"""Testing Unicode."""
import binascii

import dnstwister.tools as tools


def test_encode_ascii_domain():
    assert tools.encode_domain('www.example.com') == '7777772e6578616d706c652e636f6d'


def test_encode_unicode_domain():
    unicode_domain = u'www.\u0454xampl\u0454.com'
    punycode_domain = 'www.xn--{}.com'.format(unicode_domain.encode('punycode'))

    assert punycode_domain == 'www.xn--www.xampl.com-ehlf.com'
    assert binascii.hexlify(punycode_domain) == '7777772e786e2d2d7777772e78616d706c2e636f6d2d65686c662e636f6d'

    assert tools.encode_domain(unicode_domain) == '7777772e786e2d2d7777772e78616d706c2e636f6d2d65686c662e636f6d'


def test_encode_punycoded_domain():
    punycode_domain = 'www.xampl.com-ehlf'

    assert tools.encode_domain(punycode_domain) == '7777772e78616d706c2e636f6d2d65686c66'


def test_decode_encoded_ascii_domain():
    assert tools.decode_domain('7777772e6578616d706c652e636f6d') == 'www.example.com'


def test_decode_encoded_invalid_ascii_domain():
    """Weird edge cases with non-domains."""
    assert tools.encode_domain('example') == '6578616d706c65'
    assert tools.decode_domain('6578616d706c65') == 'example'
    assert tools.decode_domain(u'6578616d706c65') == 'example'


def test_decode_encoded_unicode_punycoded_domain():
    assert tools.decode_domain('786e2d2d7777772e78616d706c2e636f6d2d65686c66') == u'www.\u0454xampl\u0454.com'
