"""Test of when people enter brands - eg "Voltswagen AG" instead of a domain.
"""
import binascii


def test_brand(webapp):
    """Test a search for a brand brings up suggested domains."""
    query = 'Voltswagen AG'

#    response = webapp.post('/search', {'domains': query})
