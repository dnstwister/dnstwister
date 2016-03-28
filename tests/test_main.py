""" Tests of the main module.
"""
import binascii
import flask.ext.webtest
import mock
import unittest

import dnstwister
import patches


class TestMain(unittest.TestCase):
    """ Tests of the main module.
    """
    def setUp(self):
        """ Set up the mock memcache.
        """
        # Create a webtest Test App for use
        self.app = flask.ext.webtest.TestApp(dnstwister.app)

    def test_index(self):
        """ Test the index page
        """
        res = self.app.get('/')

        self.assertEqual(res.status_int, 200)
        self.assertTrue(
            'Domain name permutation engine' in res.body,
            'Page loaded HTML AOK'
        )

    @mock.patch('dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer)
    def test_report_lists_valid_domains(self):
        """ Test that the report page lists (only) valid domains.
        """
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

    @mock.patch('dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer)
    def test_report_redirect(self):
        """Test the /report?q= urls redirect to the new urls."""

        res = self.app.get('/report?q={}'.format(','.join((
            binascii.hexlify('a.com'),
            binascii.hexlify('b.com'),
        ))))

        self.assertEqual(
            'http://localhost:80/search/612e636f6d,622e636f6d',
            res.location
        )

        res = self.app.post('/search', { 'domains': 'b.com c.com' })

        self.assertEqual(
            'http://localhost:80/search/622e636f6d,632e636f6d',
            res.location
        )

    @mock.patch('dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer)
    def test_max_url_length(self):
        """If too many domains are entered to make a nice GET URL, the report
        is done without the URL.
        """
        domains = ' '.join(['www.example{}.com'.format(i)
                            for i
                            in range(9)])

        res = self.app.post('/search', { 'domains': domains })

        # We don't change location.
        assert res.location is None

        # And we have all the domains listed.
        assert all([domain in res.body
                    for domain
                    in domains])

        # We don't show exports when we have no url
        assert 'json' not in res.body

    @mock.patch('dnstwister.tools.dnstwist.DomainFuzzer', patches.SimpleFuzzer)
    def test_exports(self):
        """We have export links."""
        res = self.app.get('/search/{}'.format(binascii.hexlify('a.com')))

        assert 'json' in res.body
