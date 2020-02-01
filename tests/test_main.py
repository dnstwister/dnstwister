""" Tests of the main module.
"""
import binascii
import flask_webtest
import mock
import unittest

import dnstwister
import patches
from dnstwister.core.domain import Domain


class TestMain(unittest.TestCase):
    """ Tests of the main module.
    """
    def setUp(self):
        # Create a webtest Test App for use
        self.app = flask_webtest.TestApp(dnstwister.app)

    def test_index(self):
        """ Test the index page
        """
        res = self.app.get('/')

        self.assertEqual(res.status_int, 200)
        self.assertTrue(
            'Domain name permutation engine' in res.text,
            'Page loaded HTML AOK'
        )
