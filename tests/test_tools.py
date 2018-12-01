"""Tests of the tools module."""
import binascii
import operator
import unittest

import dnstwister.dnstwist as dnstwist
import dnstwister.tools as tools


class TestTools(unittest.TestCase):
    """Tests of the tools module."""
    def test_parse_domain(self):
        """Tests of the helper that decodes and validates a domain.

        Function returns a valid domain or None.
        """
        self.assertIs(
            None, tools.parse_domain(''),
            'Missing hex data should return None'
        )

        self.assertIs(
            None, tools.parse_domain(None),
            'Non-hex-decodable data should return None'
        )
        self.assertIs(
            None, tools.parse_domain('he378a -- ?'),
            'Non-hex-decodable data should return None'
        )

        bad_domain = '\\www.z.comasfff'
        self.assertFalse(
            dnstwist.is_valid_domain(bad_domain),
            'Bad domain should be invalid'
        )

        bad_domain_data = binascii.hexlify(bad_domain)
        self.assertIs(
            None, tools.parse_domain(bad_domain_data),
            'hex-decodable (but invalid) domain data should return None'
        )

        domain = 'www.example.com'
        self.assertTrue(
            dnstwist.is_valid_domain(domain),
            'Good domain should be valid'
        )

        domain_data = binascii.hexlify(domain)
        self.assertEqual(
            'www.example.com',
            tools.parse_domain(domain_data),
            'hex-decodable valid domain data should be returned'
        )

    def test_analyse(self):
        """Test the tool that generates the reports."""
        domain = 'a.com'
        results = tools.analyse(domain)

        self.assertEqual(
            'a.com', results[0],
            'First item in results should be the original domain'
        )

        self.assertEqual(
            ['fuzzy_domains'],
            results[1].keys(),
            'We only return fuzzy domains in report'
        )

        self.assertItemsEqual(
            {'domain-name': 'a.com', 'fuzzer': 'Original*', 'hex': 'YS5jb20='},
            results[1]['fuzzy_domains'][0],
            'First result is the original domain'
        )

        results = map(operator.itemgetter('domain-name'), results[1]['fuzzy_domains'])
        assert results == [
            'a.com', 'aa.com', 'ab.com', 'ac.com', 'ad.com', 'ae.com',
            'af.com', 'ag.com', 'ah.com', 'ai.com', 'aj.com', 'ak.com',
            'al.com', 'am.com', 'an.com', 'ao.com', 'ap.com', 'aq.com',
            'ar.com', 'as.com', 'at.com', 'au.com', 'av.com', 'aw.com',
            'ax.com', 'ay.com', 'az.com', 'c.com', 'e.com', 'i.com',
            'q.com', '1.com', 's.com', '2.com', 'w.com', 'y.com', 'z.com',
            'u.com', 'o.com', 'wwa.com', 'wwwa.com', 'www-a.com', 'acom.com',
        ]

        self.assertIs(
            None, tools.analyse('\\.38iusd-s-da   aswd?'),
            'Invalid domains return None'
        )


def test_resolve_validation():
    """Resolve validates first."""
    assert tools.resolve(',saoi9w3k490q2k4') == (False, True)


def test_encode_bonkers_unicode():
    """Some unicode is not "valid"."""
    unicode_domain = u'a\uDFFFa.com'
    assert tools.encode_domain(unicode_domain) is None
