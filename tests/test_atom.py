"""Tests of the atom behaviour."""
import base64
import flask.ext.webtest
import unittest

import dnstwister.main

class TestAtom(unittest.TestCase):
    """Tests of the atom feed behaviour."""
    def setUp(self):
        """Set up the mock memcache."""
        # Create a webtest Test App for use
        self.app = flask.ext.webtest.TestApp(dnstwister.main.app)

    def test_new_feed(self):
        """Tests the registration of a new feed."""

        # We need a domain to get the feed for.
        domain = 'www.example.com'
