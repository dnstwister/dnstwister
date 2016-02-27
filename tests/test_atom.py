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

        # Clear the webapp cache
        dnstwister.main.cache.clear()

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
                <content type="html">&lt;p&gt;
                This is the placeholder for your DNS Twister report for www.example.com.
            &lt;/p&gt;
            &lt;p&gt;
                Your first report will be generated within 24 hours with all entries
                marked as &quot;NEW&quot;.
            &lt;/p&gt;
            &lt;p&gt;
                &lt;strong&gt;Important:&lt;/strong&gt; The &quot;delta&quot; between each report is generated
                every 24 hours. If your feed reader polls this feed less often than that,
                you will miss out on changes.
            &lt;/p&gt;</content>
              </entry>
            </feed>
        """).strip().format(
            date_today=datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        # Clear the webapp cache
        dnstwister.main.cache.clear()

        # Until the first delta is actually created, this placeholder remains.
        res = self.app.get('/atom/{}'.format(base64.b64encode(domain)))
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
                <content type="html">&lt;p&gt;
                This is the placeholder for your DNS Twister report for www.example.com.
            &lt;/p&gt;
            &lt;p&gt;
                Your first report will be generated within 24 hours with all entries
                marked as &quot;NEW&quot;.
            &lt;/p&gt;
            &lt;p&gt;
                &lt;strong&gt;Important:&lt;/strong&gt; The &quot;delta&quot; between each report is generated
                every 24 hours. If your feed reader polls this feed less often than that,
                you will miss out on changes.
            &lt;/p&gt;</content>
              </entry>
            </feed>
        """).strip().format(
            date_today=datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        # We can calculate a delta though - in this case we'll place it
        # directly in the database.
        update_date = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        patches.deltas.set(domain, {
            'new': [('www.examp1e.com', '127.0.0.1')],
            'updated': [],
            'deleted': []
        }, update_date)

        # Clear the webapp cache
        dnstwister.main.cache.clear()

        res = self.app.get('/atom/{}'.format(base64.b64encode(domain)))
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
                <title type="text">NEW: www.examp1e.com</title>
                <id>new:www.examp1e.com:127.0.0.1:{secs_today}</id>
                <updated>{date_today}</updated>
                <published>{date_today}</published>
                <author>
                  <name>DNS Twister</name>
                </author>
                <content type="text">IP: 127.0.0.1</content>
              </entry>
            </feed>
        """).strip().format(
            date_today=update_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            secs_today=(
                update_date - datetime.datetime(1970, 1, 1)
            ).total_seconds()
        )
