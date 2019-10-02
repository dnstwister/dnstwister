"""Test root-served files work from the static directory."""
def test_favicon(webapp):
    """Test the favicon is loaded."""
    with open('dnstwister/static/favicon.ico', 'rb') as faviconf:
        expected_file = faviconf.read()

    assert webapp.get('/favicon.ico').body == expected_file
