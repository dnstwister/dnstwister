"""Google Safebrowsing integration test."""


def test_safebrowsing_query(webapp):
    request = webapp.get('/api/safebrowsing/dnstwister.report')

    assert request.status_code == 200

    assert request.json == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': u'646e73747769737465722e7265706f7274',
        u'fuzz_url': u'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        u'issue_detected': False,
        u'parked_score_url': u'http://localhost:80/api/parked/646e73747769737465722e7265706f7274',
        u'resolve_ip_url': u'http://localhost:80/api/ip/646e73747769737465722e7265706f7274',
        u'url': u'http://localhost:80/api/safebrowsing/dnstwister.report'
    }
