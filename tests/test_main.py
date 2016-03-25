""" Tests of the main module.
"""
import base64
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

        # Follow the 302 to the report page
        res = res.follow()
        html = res.html

        # Find the list of reported-on domains
        domains = html.find(class_='domains').text

        # Check we only have one
        self.assertTrue('www.example1.com' in domains)
        self.assertFalse('www/example2/.com' in domains)

    def test_report_redirect(self):
        """Test the /report?q= urls redirect to the new urls."""

        res = self.app.get('/report?q={}'.format(','.join((
            base64.b64encode('a.com'),
            base64.b64encode('b.com'),
        ))))

        self.assertEqual(
            'http://localhost:80/YS5jb20=,Yi5jb20=',
            res.location
        )

        res = self.app.post('/', { 'domains': 'b.com c.com' })

        self.assertEqual(
            'http://localhost:80/Yi5jb20=,Yy5jb20=',
            res.location
        )
