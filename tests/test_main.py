""" Tests of the main module.
"""
import unittest
import webapp2
import dnstwister.main


class TestMain(unittest.TestCase):
    """ Tests of the main module.
    """
    def setUp(self):
        """ Set up the mock memcache.
        """
        # Ensure the templates load
        dnstwister.main.JINJA_ENVIRONMENT.loader.searchpath = [
            'dnstwister/templates'
        ]

    def test_index(self):
        """ Test the index page
        """
        request = webapp2.Request.blank('/')
        response = request.get_response(dnstwister.main.app)

        self.assertEqual(response.status_int, 200)
        self.assertTrue(
            '<h1>DNS Twister</h1>' in response.body,
            'Page loaded HTML AOK'
        )
