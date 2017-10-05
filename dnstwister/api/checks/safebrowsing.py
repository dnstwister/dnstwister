"""Google Safe Browsing API client."""
import json
import re
import requests


API_URL = 'https://www.google.com/transparencyreport/api/v3/safebrowsing/status'


def get_report(domain):
    """Returns a Google Safe Browsing API report.

    Currently built against v4 of their API.

    Returns a count of matches.
    """
    data = {
        'site': domain
    }

    result = requests.get(API_URL, params=data)

    result_array = re.search(
        r'(\["sb.ssr".*\])',
        result.text,
        flags=re.MULTILINE).groups()[0]

    payload = r'{{"result": {}}}'.format(
        result_array
    )

    # TODO: Work out detailed meaning of these values.
    if json.loads(payload)['result'][2:-1] == [0, 0, 0, 0, 0, 0]:
        return 0

    return 1
