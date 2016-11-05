"""Test error indexes."""
def test_error_indexes(webapp):
    """Test the error indexes."""
    assert webapp.get('/').body == webapp.get('/error/99').body
