"""Whois integration test."""


def test_whois_query(webapp):
    request = webapp.get('/api/whois/dnstwister.report')

    assert request.status_code == 200

    payload = request.json
    whois_text = payload['whois_text']

    del payload['whois_text']

    assert payload == {
        u'domain': u'dnstwister.report',
        u'domain_as_hexadecimal': u'646e73747769737465722e7265706f7274',
        u'fuzz_url': u'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        u'parked_score_url': u'http://localhost:80/api/parked/646e73747769737465722e7265706f7274',
        u'resolve_ip_url': u'http://localhost:80/api/ip/646e73747769737465722e7265706f7274',
        u'url': u'http://localhost:80/api/whois/dnstwister.report',
    }

    assert 'Robert Wallhead' in whois_text
