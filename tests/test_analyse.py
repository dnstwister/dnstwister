"""Test analysis page."""
import pytest
import webtest.app


def test_analysis(webapp):
    """Test we can analyse a page."""
    response = webapp.get('/analyse/646e73747769737465722e7265706f7274')

    assert response.status_code == 200
    assert 'Use these tools to safely analyse <strong>dnstwister.report</strong>' in response.text


def test_bad_domain_fails(webapp):
    """Test the analyse page checks domain validity."""
    with pytest.raises(webtest.app.AppError) as err:
        webapp.get('/analyse/3234jskdnfsdf7y34')
    assert '400 BAD REQUEST' in str(err)
