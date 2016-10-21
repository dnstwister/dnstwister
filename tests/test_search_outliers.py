"""Test of weird search behaviours."""
import binascii


def test_no_domains_key(webapp):
    """Test a POST without 'domains' being set fails."""
    response = webapp.post('/search')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/2'


def test_empty_domains_key(webapp):
    """Test a POST with 'domains' being set to whitespace fails."""
    response = webapp.post('/search', {'domains': ' '})

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/2'


def test_no_valid_domains(webapp):
    """Test that submitting no valid domains fails."""
    response = webapp.post('/search', {'domains': '...'})

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/0'


def test_suggestion(webapp):
    """Test that submitting no valid domains fails.

    Where a domain could be suggested, it is.
    """
    response = webapp.post('/search', {'domains': 'example'})

    assert response.status_code == 302

    domain = 'example.com'
    enc_domain = binascii.hexlify(domain)
    expected_redirect = 'http://localhost:80/error/0?suggestion=' + enc_domain
    assert response.headers['location'] == expected_redirect


def test_no_suggestion_long_words(webapp):
    """Test long search terms are dropped in suggestions."""
    query = 'jsdfijsdlfkjsoijsldjlsdkjflskdjfoewjfsdfldkishgisuehgdsfsdkf'
    response = webapp.post('/search', {'domains': query})

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/0'

    query = (
        'jsdfijsdlfkjsoijsldjlsdkjflskdjfoewjfsdfldkishgisuehgdsfs dkf'
    )
    response = webapp.post('/search', {'domains': query})

    assert response.status_code == 302
    assert response.headers['location'].endswith('=646b662e636f6d')
    assert binascii.unhexlify('646b662e636f6d') == 'dkf.com'


def test_no_valid_domains_only(webapp):
    """Test invalid domains not in suggestions."""
    query = 'abc ?@<>.'
    response = webapp.post('/search', {'domains': query})

    assert response.status_code == 302
    assert response.headers['location'].endswith('=6162632e636f6d')
    assert binascii.unhexlify('6162632e636f6d') == 'abc.com'


def test_suggestion_rendered(webapp):
    """Test suggestion rendered on index."""
    response = webapp.post('/search', {'domains': 'example'})
    next_url = response.headers['location']
    response = webapp.get(next_url)

    assert 'example.com' in response.body


def test_get_errors(webapp):
    """Test funny URLs for a GET search."""
    response = webapp.get('/search/__<<>')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/0'

