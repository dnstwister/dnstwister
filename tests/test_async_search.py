"""Testing the new async search."""
import binascii


def test_feature_flag_not_true_uses_old_search(webapp):
    """By default the old search is used."""
    domain = 'a.com'
    response = webapp.post('/search', {'domains': domain})

    assert response.headers['location'] == 'http://localhost:80/search/612e636f6d'


def test_feature_flag_set_to_true_uses_new_search(webapp, monkeypatch):
    """A value of 'true' enables the new search."""
    monkeypatch.setenv('feature.async_search', 'true')

    domain = 'a.com'
    response = webapp.post('/search', {'domains': domain})

    assert response.headers['location'] == 'http://localhost:80/search?ed=612e636f6d'


def test_feature_flag_set_to_true_redirects_get_urls(webapp, monkeypatch):
    """A value of 'true' enables the new search."""
    monkeypatch.setenv('feature.async_search', 'true')

    domain = 'a.com'
    response = webapp.get('/search/{}'.format(binascii.hexlify(domain)))

    assert response.headers['location'] == 'http://localhost:80/search?ed=612e636f6d'


def test_feature_flag_not_true_does_not_redirect_get_urls(webapp, monkeypatch):
    """A value of 'true' enables the new search."""
    domain = 'a.com'
    response = webapp.get('/search/{}'.format(binascii.hexlify(domain)))

    # Not a redirect.
    assert response.status_code == 200
