"""Test analysis page."""


def test_analysis(webapp):
    """Test we can analyse a page."""
    response = webapp.get('/analyse/646e73747769737465722e7265706f7274')

    assert response.status_code == 200
    assert 'Use these tools to safely analyse dnstwister.report' in response.body
