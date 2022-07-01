"""Test of weird search behaviours."""
# -*- coding: utf-8 -*-
import binascii

from dnstwister.core.domain import Domain


def test_no_domains_key(webapp):
    """Test a POST without 'domains' being set fails."""
    response = webapp.post('/search', expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'] == '/error/2'


def test_empty_domains_key(webapp):
    """Test a POST with 'domains' being set to whitespace fails."""
    response = webapp.post('/search', {'domains': ' '}, expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'] == '/error/2'


def test_suggestion(webapp):
    """Test that submitting no valid domains fails.

    Where a domain could be reasonably suggested, it is.
    """
    response = webapp.post('/search', {'domains': 'example'}, expect_errors=True)

    assert response.status_code == 302

    domain = 'example.com'
    enc_domain = Domain(domain).to_hex()
    expected_redirect = '/error/0?suggestion=' + enc_domain
    assert response.headers['location'] == expected_redirect


def test_no_valid_domains_only(webapp):
    """Test invalid domains not in suggestions."""
    query = 'abc ?@<>.'
    response = webapp.post('/search', {'domains': query}, expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'].endswith('=6162632e636f6d')
    assert binascii.unhexlify('6162632e636f6d').decode() == 'abc.com'


def test_suggestion_rendered(webapp):
    """Test suggestion rendered on index."""
    response = webapp.post('/search', {'domains': 'example'}, expect_errors=True).follow()

    assert 'example.com' in response.text


def test_get_errors(webapp):
    """Test funny URLs for a GET search."""
    response = webapp.get('/search/__<<>', expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'] == '/error/0'


def test_no_suggestion_many_words(webapp):
    """Test many search terms are dropped in suggestions."""
    query = 'j s d f i j s'
    response = webapp.post('/search', {'domains': query}, expect_errors=True)

    assert response.status_code == 302
    assert response.headers['location'] == '/error/0'


def test_suggestion_bad_data(webapp):
    """Test that submitting invalid data in suggestion doesn't crash the page.
    """
    response = webapp.get('/error/0?suggestion')
    assert response.status_code == 200

    response = webapp.get('/error/0?suggestion=')
    assert response.status_code == 200

    response = webapp.get('/error/0?suggestion=sdlkfjsdlfkjsdf')
    assert response.status_code == 200

    response = webapp.get('/error/0?suggestion=<script>...<?')
    assert response.status_code == 200

    response = webapp.get('/error/0?suggestion=a.com&cat=2')
    assert response.status_code == 200


def test_whitespace_trimmed(webapp):
    """Tabs and spaces are cleaned up first."""
    domain = "  icloudstats.net\t\r  \n"

    response = webapp.post('/search', {'domains': domain}).follow()
    assert response.status_code == 200
    assert response.request.url == 'http://localhost/search/{}'.format(Domain('icloudstats.net').to_hex())


def test_fix_comma_typo(webapp):
    """Test accidentally entering in a comma instead of period is corrected.
    """
    malformed_domain = 'example,com'
    expected_suggestion = 'example.com'

    response = webapp.post('/search', {'domains': malformed_domain}, expect_errors=True).follow()

    assert expected_suggestion in response.text


def test_fix_slash_typo(webapp):
    """Test accidentally entering in a slash instead of period is corrected.
    """
    malformed_domain = 'example/com'
    expected_suggestion = 'example.com'

    response = webapp.post('/search', {'domains': malformed_domain}, expect_errors=True).follow()

    assert expected_suggestion in response.text


def test_fix_space_typo(webapp):
    """Test accidentally entering in a space instead of period is corrected.
    """
    malformed_domain = 'example com'
    expected_suggestion = 'example.com'

    response = webapp.post('/search', {'domains': malformed_domain}, expect_errors=True).follow()

    assert expected_suggestion in response.text


def test_post_unicode(webapp):
    """Test of end-to-end unicode."""
    unicode_domain = 'höt.com'

    expected_punycode = 'xn--ht-fka.com'
    expected_hex = Domain(expected_punycode).to_hex()

    assert expected_hex == '786e2d2d68742d666b612e636f6d'

    response = webapp.post('/search', {'domains': unicode_domain}).follow()

    assert response.status_code == 200
    assert response.request.url == 'http://localhost/search/{}'.format(expected_hex)
    assert unicode_domain in response.text

    assert 'höt.com (xn--ht-fka.com)' in response.text
