"""Whois integration test."""


def test_whois_query(webapp):
    request = webapp.get('/api/whois/dnstwister.report')

    assert request.status_code == 200

    payload = request.json
    whois_text = payload['whois_text']

    del payload['whois_text']

    assert payload == {
        'domain': 'dnstwister.report',
        'domain_as_hexadecimal': '646e73747769737465722e7265706f7274',
        'fuzz_url': 'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        'parked_score_url': 'http://localhost:80/api/parked/646e73747769737465722e7265706f7274',
        'resolve_ip_url': 'http://localhost:80/api/ip/646e73747769737465722e7265706f7274',
        'url': 'http://localhost:80/api/whois/dnstwister.report',
    }

    assert 'Robert Wallhead' in whois_text
