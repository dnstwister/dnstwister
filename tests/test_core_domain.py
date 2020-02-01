import pytest

from dnstwister.core.domain import Domain, InvalidDomainException



def test_can_take_explicit_unicode_domain():
    assert Domain(u'hello.com').to_ascii() == 'hello.com'


def test_can_take_explicit_unicode_idna_domain():
    assert Domain(u'xn--w5a.com').to_ascii() == 'xn--w5a.com'


def test_can_take_explicit_unicode_unicode_domain():
    assert Domain(u'ӓ.com').to_ascii() == 'xn--w5a.com'
    assert Domain(u'www.\u0454xample.com').to_ascii() == 'www.xn--xample-9uf.com'


def test_can_take_bytes_domain():
    assert Domain(b'hello.com').to_ascii() == 'hello.com'


def test_can_take_bytes_idna_domain():
    assert Domain(b'xn--w5a.com').to_ascii() == 'xn--w5a.com'


def test_can_take_idna_domain():
    assert Domain('xn--w5a.com').to_ascii() == 'xn--w5a.com'
    assert Domain('xn--xample-hye.com').to_unicode() == 'εxample.com'


def test_can_take_unicode_domain():
    assert Domain('ӓ.com').to_ascii() == 'xn--w5a.com'


def test_can_return_unicode_domain():
    assert Domain('xn--w5a.com').to_unicode() == 'ӓ.com'
    assert Domain('a.com').to_unicode() == 'a.com'


def test_can_return_hex_repr_of_domain():
    assert Domain('xn--w5a.com').to_hex() == '786e2d2d7735612e636f6d'
    assert Domain('ӓ.com').to_hex() == '786e2d2d7735612e636f6d'
    assert Domain('a.com').to_hex() == '612e636f6d'
    assert Domain(b'a.com').to_hex() == '612e636f6d'


def test_can_return_pretty_version_of_domain():
    assert str(Domain('a.com')) == 'a.com'
    assert str(Domain('ӓ.com')) == 'ӓ.com (xn--w5a.com)'
    assert f"{Domain('ӓ.com')}" == 'ӓ.com (xn--w5a.com)'
    assert '{}'.format(Domain('ӓ.com')) == 'ӓ.com (xn--w5a.com)'


def test_invalid_domain_raises_exception():
    with pytest.raises(InvalidDomainException):
        Domain(1)

    with pytest.raises(InvalidDomainException):
        Domain('')

    with pytest.raises(InvalidDomainException):
        Domain('?@?!#?!?23//d/sad')

    with pytest.raises(InvalidDomainException):
        Domain(None)

    with pytest.raises(InvalidDomainException):
        Domain(u'a\uDFFFa.com')


def test_can_try_parse():
    assert Domain.try_parse('?@?!#?!?23//d/sad') is None
    assert Domain.try_parse('xn--w5a.com') == Domain('xn--w5a.com')


def test_can_make_domain_from_domain():
    assert Domain(Domain('ӓ.com')).to_ascii() == 'xn--w5a.com'


def test_can_compare_domains():
    assert Domain('ӓ.com') == Domain('xn--w5a.com')


def test_can_compare_domain_instance_to_valid_strings():
    assert Domain('ӓ.com') == 'xn--w5a.com'
    assert Domain('ӓ.com') == u'xn--w5a.com'
    assert Domain('ӓ.com') == b'xn--w5a.com'
    assert Domain('ӓ.com') == 'ӓ.com'

    assert Domain('ӓ.com') != 'blob'
    assert Domain('ӓ.com') != 2
    assert Domain('ӓ.com') != None


def test_uses_idna_2008_encoding():
    """We need to be using the IDNA 2008 encoding to be up to date and that
    means we need the idna module, not just pure Python.

    Python squashes that down to 'strasse.de' because if uses pre-2008 IDNA
    encoding.
    """
    assert 'straße.de'.encode('idna').decode() == 'strasse.de'
    assert Domain('straße.de').to_ascii() == 'xn--strae-oqa.de'

