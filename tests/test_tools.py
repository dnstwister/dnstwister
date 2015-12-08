""" Tests of the tools module.
"""
import tools
import unittest


class TestTools(unittest.TestCase):
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
