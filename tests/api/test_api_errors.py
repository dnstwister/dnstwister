"""Test custom error pages."""
def test_404_error(webapp):
    page = webapp.get('/api/nosuchluck', expect_errors=True)

    assert page.status_code == 404
    assert page.json == {'error': 'Resource not found.'}


def test_400_error(webapp):
    page = webapp.get('/api/fuzz/notahexdomain', expect_errors=True)

    assert page.status_code == 400
    assert page.json == {'error': 'Malformed domain or domain not represented in hexadecimal format.'}
