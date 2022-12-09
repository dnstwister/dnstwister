"""Google Safe Browsing API client."""
import json
import re
import requests


API_URL = 'https://transparencyreport.google.com/transparencyreport/api/v3/safebrowsing/status'


def get_report(domain):
    """Returns a Google Safe Browsing API report.

    Hits the same endpoint as:

        https://transparencyreport.google.com/safe-browsing/search

    Returns 1 if there's an issue with the domain, 0 if not.
    """
    idna_domain = domain.to_ascii()
    data = {
        'site': idna_domain
    }

    result = requests.get(API_URL, params=data)

    # Yep, this is gross, the response value is very strangely formatted.
    result_array = re.search(
        r'(\["sb.ssr".*?\])',
        result.text,
        flags=re.MULTILINE).groups()[0]

    payload = r'{{"result": {}}}'.format(
        result_array
    )

    # TODO: Work out detailed meaning of these values.
    if json.loads(payload)['result'][2:-2] == [0, 0, 0, 0, 0]:
        return 0

    return 1
