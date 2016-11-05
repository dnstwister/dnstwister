"""Parked check integration test."""


def test_parked_query(webapp):
    """Test the parked API against our own domain."""
    request = webapp.get('/api/parked/dnstwister.report')

    assert request.status_code == 200

    assert request.json == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': u'646e73747769737465722e7265706f7274',
        u'fuzz_url': u'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        u'redirects': False,
        u'redirects_to': None,
        u'resolve_ip_url': u'http://localhost:80/api/ip/646e73747769737465722e7265706f7274',
        u'score': 0.07,
        u'score_text': u'Possibly',
        u'url': u'http://localhost:80/api/parked/dnstwister.report'
    }
