""" Tests of the tools module.
"""
import base64
import dnstwister.dnstwist as dnstwist
import dnstwister.tools as tools
import operator
import unittest


class TestTools(unittest.TestCase):
    """ Tests of the tools module.
    """
    def test_query_domains(self):
        """ Test the helper that splits up the domains query into a list of
            domains.
        """
        self.assertIs(
            None, tools.query_domains({}), 'Missing domains key'
        )

        self.assertIs(
            None, tools.query_domains({'blah': 'cat'}), 'Missing domains key'
        )

        inp = 'www.example.com'

        self.assertEqual(
            ['www.example.com'],
            tools.query_domains({'domains': inp}),
            'One domain',
        )

        inp = '\n\n\n\n\n          www.example.com         \n\n\n\n\n'

        self.assertEqual(
            ['www.example.com'],
            tools.query_domains({'domains': inp}),
            'One domain',
        )

        inp = """

            www.example.com

            www.example2.com

            www.example2.com

        """

        self.assertItemsEqual(
            ['www.example.com', 'www.example2.com'],
            tools.query_domains({'domains': inp}),
            'Two domains, duplicates and whitespace ignored',
        )

        inp = """  www.example.com ,   www.example2.com\t, www.example3.com \r\n  \t"""

        self.assertItemsEqual(
            ['www.example.com', 'www.example2.com', 'www.example3.com'],
            tools.query_domains({'domains': inp}),
            'Three domains, commas treated as tabs as whitespace',
        )

        inp = "a.com, b.com c.com"

        self.assertItemsEqual(
            ['a.com', 'b.com', 'c.com'],
            tools.query_domains({'domains': inp}),
        )

        inp = u"""

            www.example.com\r\n

            www.example2.com

            www.example2.com

        """

        self.assertItemsEqual(
            ['www.example.com', 'www.example2.com'],
            tools.query_domains({'domains': inp}),
            'Unicode and Windows newlines not handled',
        )


    def test_parse_domain(self):
        """ Tests of the helper that decodes and validates a domain.

            Function returns a valid domain or None.
        """
        self.assertIs(
            None, tools.parse_domain(''),
            'Missing b64 data should return None'
        )

        self.assertIs(
            None, tools.parse_domain(None),
            'Non-b64-decodable data should return None'
        )
        self.assertIs(
            None, tools.parse_domain('he378a -- ?'),
            'Non-b64-decodable data should return None'
        )

        bad_domain = '\\www.z.comasfff'
        self.assertFalse(
            dnstwist.validate_domain(bad_domain),
            'Bad domain should be invalid'
        )

        bad_domain_data = base64.b64encode(bad_domain)
        self.assertIs(
            None, tools.parse_domain(bad_domain_data),
            'b64-decodable (but invalid) domain data should return None'
        )

        domain = 'www.example.com'
        self.assertTrue(
            dnstwist.validate_domain(domain),
            'Good domain should be valid'
        )

        domain_data = base64.b64encode(domain)
        self.assertEqual(
            'www.example.com',
            tools.parse_domain(domain_data),
            'b64-decodable valid domain data should be returned'
        )


    def test_analyse(self):
        """ Test the tool that generates the reports.
        """
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
            {'domain-name': 'a.com', 'fuzzer': 'Original*', 'b64': 'YS5jb20='},
            results[1]['fuzzy_domains'][0],
            'First result is the original domain'
        )

        self.assertItemsEqual(
            [
                'a.com', 'aa.com', 'ab.com', 'ac.com', 'ad.com', 'ae.com',
                'af.com', 'ag.com', 'ah.com', 'ai.com', 'aj.com', 'ak.com',
                'al.com', 'am.com', 'an.com', 'ao.com', 'ap.com', 'aq.com',
                'ar.com', 'as.com', 'at.com', 'au.com', 'av.com', 'aw.com',
                'ax.com', 'ay.com', 'az.com', 'c.com', 'e.com', 'i.com',
                'q.com', '1.com', 's.com', '2.com', 'w.com', 'y.com', 'z.com',
                'wwa.com', 'wwwa.com', 'www-a.com', 'acom.com'
            ],
            map(operator.itemgetter('domain-name'), results[1]['fuzzy_domains']),
            'We have 41 results including the original domain'
        )

        self.assertIs(
            None, tools.analyse('\\.38iusd-s-da   aswd?'),
            'Invalid domains return None'
        )
