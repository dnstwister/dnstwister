"""Google Safe Browsing API client."""
import json
import re
import requests


API_URL = 'https://www.google.com/safebrowsing/diagnostic'


def get_report(domain):
    """Returns a Google Safe Browsing API report.

    Currently built against v4 of their API.

    Returns a count of matches.
    """
    data = {
        'output': 'jsonp',
        'site': domain
    }

    result = requests.get(API_URL, params=data)

    json_result = json.loads(re.search(r'({.*})', result.text).groups()[0])

    status = json_result['website']['malwareListStatus']

    if status == 'unlisted':
        return 0

    return 1
