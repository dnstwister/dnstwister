"""Parked domain detection."""
import requests

import shared


def _domain_redirects(domain, path=''):
    """Returns whether a domain (and optional path) redirects to another."""
    req = requests.get(
        'http://{}/{}'.format(domain, path),
        **shared.REQ_KWARGS
    )
    landed_domain = shared.get_domain(req.url)
    return landed_domain != domain, landed_domain


def get_score(domain):
    """Takes a punt as to whether a domain is parked or not.

    Returns a score between 0 and 1 as to the likelihood that the domain is
    parked. 1 = highly likely.
    """
    score = 0

    redirects, landed_domain1 = _domain_redirects(domain)
    if redirects:
        score += 1

    redirects, landed_domain2 = _domain_redirects(
        domain, 'dnstwister_parked_check'
    )

    if redirects:
        score += 1

    if landed_domain1 == landed_domain2:
        score += 1

    return round(score / 3.0, 2)
