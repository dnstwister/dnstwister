"""Test root-served files work from the static directory."""
def test_robots_txt(webapp):
    """Test the robots.txt is loaded."""
    with open('dnstwister/static/robots.txt', 'rb') as robotsf:
        expected_file = robotsf.read()

    assert webapp.get('/robots.txt').body == expected_file
