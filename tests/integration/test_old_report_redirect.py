"""Test old search links work.

e.g: /report?q=dnstwister.report goes to /search/dnstwister.report
"""


def test_redirect(webapp):
    """Test we can redirect."""
    response = webapp.get('/report?q=dnstwister.report')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/search/dnstwister.report'


def test_no_redirect(webapp):
    """Test we only redirect where valid."""
    response = webapp.get('/report?p=3')

    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost:80/error/1'
