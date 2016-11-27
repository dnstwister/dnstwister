"""Google Safebrowsing integration test."""


def test_safebrowsing_query(webapp):
    """Test our domain is safe."""
    response = webapp.get('/api/safebrowsing/dnstwister.report')

    assert response.status_code == 200

    assert response.json == {
        'domain': 'dnstwister.report',
        'domain_as_hexadecimal': '646e73747769737465722e7265706f7274',
        'fuzz_url': 'http://localhost:80/api/fuzz/646e73747769737465722e7265706f7274',
        'issue_detected': False,
        'parked_score_url': 'http://localhost:80/api/parked/646e73747769737465722e7265706f7274',
        'resolve_ip_url': 'http://localhost:80/api/ip/646e73747769737465722e7265706f7274',
        'url': 'http://localhost:80/api/safebrowsing/dnstwister.report'
    }


def test_safebrowsing_with_bad_domain(webapp):
    """Test against the google test domain (malware.testing.google.test)."""
    response = webapp.get('/api/safebrowsing/malware.testing.google.test')

    assert response.status_code == 200
    assert response.json['issue_detected'] is True
