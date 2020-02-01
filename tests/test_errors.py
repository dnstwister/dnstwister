"""Test custom error pages."""
def test_404_error(webapp):
    page = webapp.get('/nosuchluck', expect_errors=True)

    assert page.status_code == 404
    assert 'Unfortunately the page you are looking for could not be found' in page.text
    assert 'index.min.css' in page.text


def test_400_error(webapp):
    page = webapp.get('/search/6161612e636f6d/ggg', expect_errors=True)

    assert page.status_code == 400
    assert 'Unknown export format' in page.text
    assert 'index.min.css' in page.text
