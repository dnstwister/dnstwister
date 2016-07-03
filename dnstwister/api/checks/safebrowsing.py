"""Google Safe Browsing API client."""
import json
import os
import requests


API_URL = 'https://safebrowsing.googleapis.com/v4/threatMatches:find'


def get_report(domain):
    """Returns a Google Safe Browsing API report.

    Currently built against v4 of their API.

    Returns a count of matches.
    """
    api_key = os.environ['SAFEBROWSING_KEY']

    payload = {
        'client': {
            'clientId': 'dnstwister',
            'clientVersion': '1.8.2'
        },
        'threatInfo': {
            'threatTypes': [
                'MALWARE',
                'SOCIAL_ENGINEERING',
                'POTENTIALLY_HARMFUL_APPLICATION',
                'UNWANTED_SOFTWARE'
            ],
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [
                {'url': 'http://{}'.format(domain)}
            ]
        }
    }

    result = requests.post(
        API_URL,
        params={'key': api_key},
        data=json.dumps(payload),
    ).json()

    try:
        return len(result['matches'])
    except KeyError:
        return 0
