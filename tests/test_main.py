""" Tests of the main module.
"""
import flask.ext.webtest
import unittest

import dnstwister.main


class TestMain(unittest.TestCase):
    """ Tests of the main module.
    """
    def setUp(self):
        """ Set up the mock memcache.
        """
        # Create a webtest Test App for use
        self.app = flask.ext.webtest.TestApp(dnstwister.main.app)

    def test_index(self):
        """ Test the index page
        """
        # Load index page. We have to include an invalid error here to get the
        # page to load as the non-error index is static and not supported via
        # webtest.
        res = self.app.get('/error/9')

        self.assertEqual(res.status_int, 200)
        self.assertTrue(
            'Domain name permutation engine' in res.body,
            'Page loaded HTML AOK'
        )

    def test_report_lists_valid_domains(self):
        """ Test that the report page lists (only) valid domains.
        """
        # Load index page. We have to include an invalid error here to get the
        # page to load as the non-error index is static and not supported via
        # webtest.
        res = self.app.get('/error/9')

        # Fill out 2 URLs (one valid, one not) and submit to the report
        # endpoint.
        domains = """
            www.example1.com
            www/example2/com
        """
        form = res.form
        form['domains'] = domains
        res = form.submit()

        # This is a short list of domains so we have redirected to a GET url.
        # We have also dropped the invalid domain.
        self.assertEqual(
            'http://localhost:80/report?q=d3d3LmV4YW1wbGUxLmNvbQ%3D%3D',
            res.location
        )

        # Follow the 302 to the report page
        res = res.follow()
        html = res.html

        # Find the list of reported-on domains
        domains = html.find(class_='domains').text

        # Check we only have one
        self.assertTrue('www.example1.com' in domains)
        self.assertFalse('www/example2/.com' in domains)
