"""Tests of the tools module."""
import binascii
import operator
import unittest

import dnstwister.dnstwist as dnstwist
import dnstwister.tools as tools
from dnstwister.core.domain import Domain


class TestTools(unittest.TestCase):
    """Tests of the tools module."""
    def test_parse_domain(self):
        """Tests of the helper that decodes and validates a domain.

        Function returns a valid domain or None.
        """
        self.assertIs(
            None, tools.try_parse_domain_from_hex(''),
            'Missing hex data should return None'
        )

        self.assertIs(
            None, tools.try_parse_domain_from_hex(None),
            'Non-hex-decodable data should return None'
        )
        self.assertIs(
            None, tools.try_parse_domain_from_hex('he378a -- ?'),
            'Non-hex-decodable data should return None'
        )

        bad_domain = '\\www.z.comasfff'
        self.assertFalse(
            Domain.try_parse(bad_domain) is not None,
            'Bad domain should be invalid'
        )

        long_bad_domain = 'www.zsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssszssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss.com'
        self.assertFalse(
            Domain.try_parse(long_bad_domain) is not None,
            'Long domain should be invalid'
        )

        bad_domain_data = binascii.hexlify(bad_domain.encode())
        self.assertIs(
            None, tools.try_parse_domain_from_hex(bad_domain_data),
            'hex-decodable (but invalid) domain data should return None'
        )

        domain = 'www.example.com'
        self.assertTrue(
            Domain.try_parse(domain) is not None,
            'Good domain should be valid'
        )

        domain_data = binascii.hexlify(domain.encode()).decode()
        self.assertEqual(
            'www.example.com',
            tools.try_parse_domain_from_hex(domain_data),
            'hex-decodable valid domain data should be returned'
        )

    def test_analyse(self):
        """Test the tool that generates the reports."""
        domain = Domain('a.com')
        results = tools.analyse(domain)

        self.assertEqual(
            'a.com', results[0],
            'First item in results should be the original domain'
        )

        self.assertEqual(
            ['fuzzy_domains'],
            list(results[1].keys()),
            'We only return fuzzy domains in report'
        )

        assert results[1]['fuzzy_domains'][0] == {
            'domain-name': 'a.com',
            'fuzzer': 'Original*',
            'hex': '612e636f6d'
        }

        results = map(operator.itemgetter('domain-name'), results[1]['fuzzy_domains'])
        assert sorted(results) == [
            '1.com',
            '2.com',
            'a.com',
            'aa.com',
            'ab.com',
            'ac.com',
            'acom.com',
            'ad.com',
            'ae.com',
            'af.com',
            'ag.com',
            'ah.com',
            'ai.com',
            'aj.com',
            'ak.com',
            'al.com',
            'am.com',
            'an.com',
            'ao.com',
            'ap.com',
            'aq.com',
            'ar.com',
            'as.com',
            'at.com',
            'au.com',
            'av.com',
            'aw.com',
            'ax.com',
            'ay.com',
            'az.com',
            'c.com',
            'e.com',
            'i.com',
            'o.com',
            'q.com',
            's.com',
            'u.com',
            'w.com',
            'wwa.com',
            'www-a.com',
            'wwwa.com',
            'y.com',
            'z.com'
        ]


def test_encode_bonkers_unicode():
    """Some unicode is not "valid"."""
    unicode_domain = u'a\uDFFFa.com'
    assert Domain.try_parse(unicode_domain) is None
