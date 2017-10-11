"""Testing Unicode."""
import binascii

from dnstwister import dnstwist, tools


def test_encode_ascii_domain():
    assert tools.encode_domain('www.example.com') == '7777772e6578616d706c652e636f6d'


def test_encode_unicode_domain():
    unicode_domain = u'www.\u0454xampl\u0454.com'

    # www.xn--xampl-91ef.com in hex
    assert tools.encode_domain(unicode_domain) == '7777772e786e2d2d78616d706c2d393165662e636f6d'


def test_encode_punycoded_domain():
    punycode_domain = 'www.xampl.com-ehlf'

    assert tools.encode_domain(punycode_domain) == '7777772e78616d706c2e636f6d2d65686c66'


def test_decode_encoded_ascii_domain():
    assert tools.decode_domain('7777772e6578616d706c652e636f6d') == 'www.example.com'


def test_decode_encoded_invalid_ascii_domain():
    """Weird edge cases with non-domains that were causing issues."""
    assert tools.encode_domain('example') == '6578616d706c65'
    assert tools.decode_domain('6578616d706c65') == 'example'
    assert tools.decode_domain(u'6578616d706c65') == 'example'


def test_decode_encoded_unicode_punycoded_domain():

    # www.xn--xampl-91ef.com in hex
    assert tools.decode_domain('7777772e786e2d2d78616d706c2d393165662e636f6d') == u'www.\u0454xampl\u0454.com'


def test_dnstwist_validations():
    """dnstwist validates domains internally, including unicode."""
    assert dnstwist.dnstwist.validate_domain('www.example1.com')
    assert dnstwist.dnstwist.validate_domain(u'www.\u0454xampl\u0454.com')
    assert dnstwist.dnstwist.validate_domain(u'www.\u0454xampl\u0454.com')

    assert not dnstwist.dnstwist.validate_domain('www.\u0454xampl\u0454.com')
    assert not dnstwist.dnstwist.validate_domain(u'example1')
    assert not dnstwist.dnstwist.validate_domain('example1')
