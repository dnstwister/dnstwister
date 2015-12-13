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

        print tools.query_domains({'domains': inp})

        self.assertItemsEqual(
            ['www.example.com', 'www.example2.com'],
            tools.query_domains({'domains': inp}),
            'Two domains, duplicats and whitespace ignored',
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
        """ Tests of the helper that parses out a 'b64' key from the GET
            params, decodes and validates it.

            Function returns a valid domain or None.
        """
        self.assertIs(
            None, tools.parse_domain({}),
            'Missing b64 key should return None'
        )
        self.assertIs(
            None, tools.parse_domain({'hi': 'hello'}),
            'Missing b64 key should return None'
        )

        self.assertIs(
            None, tools.parse_domain({'b64': None}),
            'Non-b64-decodable b64 key should return None'
        )
        self.assertIs(
            None, tools.parse_domain({'b64': 'he378a -- ?'}),
            'Non-b64-decodable b64 key should return None'
        )

        bad_domain = '\\www.z.comasfff'
        self.assertFalse(
            dnstwist.validate_domain(bad_domain),
            'Bad domain should be invalid'
        )

        bad_domain_data = base64.b64encode(bad_domain)
        self.assertIs(
            None, tools.parse_domain({'b64': bad_domain_data}),
            'b64-decodable (but invalid) domain in b64 key should return None'
        )

        domain = 'www.example.com'
        self.assertTrue(
            dnstwist.validate_domain(domain),
            'Good domain should be valid'
        )

        domain_data = base64.b64encode(domain)
        self.assertEqual(
            'www.example.com',
            tools.parse_domain({'b64': domain_data}),
            'b64-decodable valid domain in b64 key should be returned'
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
            {'domain': 'a.com', 'fuzzer': 'Original*', 'b64': 'YS5jb20='},
            results[1]['fuzzy_domains'][0],
            'First result is the original domain'
        )

        self.assertItemsEqual(
            [
                'a.com', 'c.com', 'e.com', 'i.com', 'q.com', 'aa.com',
                'w.com', 's.com', 'z.com', 'wwwa.com'
            ],
            map(operator.itemgetter('domain'), results[1]['fuzzy_domains']),
            'We have 10 results including the original domain'
        )

        self.assertIs(
            None, tools.analyse('\\.38iusd-s-da   aswd?'),
            'Invalid domains return None'
        )
