"""Test root-served files work from the static directory."""
def test_robots_txt(webapp):
    """Test the robots.txt is loaded."""
    with open('dnstwister/static/robots.txt', 'rb') as robotsf:
        expected_file = robotsf.read()

    assert webapp.get('/robots.txt').body == expected_file


def test_security_txt(webapp):
    """Test the security.txt is loaded."""
    with open('dnstwister/static/security.txt', 'rb') as securityf:
        expected_file = securityf.read()

    assert webapp.get('/security.txt').body == expected_file
