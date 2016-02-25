"""Tests of the atom behaviour."""
import base64
import datetime
import flask.ext.webtest
import mock
import patches
import textwrap
import unittest
import xml.dom.minidom

import dnstwister.main


class TestAtom(unittest.TestCase):
    """Tests of the atom feed behaviour."""
    def setUp(self):
        """Set up the mock memcache."""
        # Reset the test databases
        patches.deltas.reset()

        # Create a webtest Test App for use
        self.app = flask.ext.webtest.TestApp(dnstwister.main.app)

    @mock.patch('dnstwister.main.storage.pg_database.deltas', patches.deltas)
    def test_new_feed(self):
        """Tests the registration of a new feed."""
        # We need a domain to get the feed for.
        domain = 'www.example.com'

        # A feed is registered by trying to load it (and it not already being
        # registered).
        res = self.app.get('/atom/{}'.format(base64.b64encode(domain)))

        # And only returns a single placeholder item.
        assert str(res) == textwrap.dedent("""
            Response: 200 OK
            Content-Type: application/atom+xml; charset=utf-8
            <?xml version="1.0" encoding="utf-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <title type="text">DNS Twister report for www.example.com</title>
              <id>https://dnstwister.report/atom/d3d3LmV4YW1wbGUuY29t</id>
              <updated>{date_today}</updated>
              <link href="https://dnstwister.report/report/?q=d3d3LmV4YW1wbGUuY29t" />
              <link href="https://dnstwister.report/atom/d3d3LmV4YW1wbGUuY29t" rel="self" />
              <generator>Werkzeug</generator>
              <entry xml:base="https://dnstwister.report/atom/d3d3LmV4YW1wbGUuY29t">
                <title type="text">No report yet for www.example.com</title>
                <id>waiting:www.example.com</id>
                <updated>{date_today}</updated>
                <published>{date_today}</published>
                <author>
                  <name>DNS Twister</name>
                </author>
                <content type="text">Your report feed will be generated within 24 hours.</content>
              </entry>
            </feed>
        """).strip().format(
            date_today=datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
        )
