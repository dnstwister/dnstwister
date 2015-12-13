""" Tests of the tools module.
"""
import base64
import dnstwister.dnstwist as dnstwist
import dnstwister.tools as tools
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
