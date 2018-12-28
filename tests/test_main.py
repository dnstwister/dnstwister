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
    def test_exports(self):
        """We have export links."""
        res = self.app.get('/search/{}'.format(binascii.hexlify('a.com')))

        assert 'json' in res.body
