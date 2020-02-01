"""Test custom error pages."""
def test_404_error(webapp):
    page = webapp.get('/nosuchluck', expect_errors=True)

    assert page.status_code == 404
    assert 'Unfortunately the page you are looking for could not be found' in page.text
    assert 'index.min.css' in page.text


def test_400_error(webapp):
    page = webapp.get('/atom/notahexdomain', expect_errors=True)

    assert page.status_code == 400
    assert 'Malformed domain or domain not represented in hexadecimal format.' in page.text
    assert 'index.min.css' in page.text
