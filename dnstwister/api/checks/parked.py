"""Parked domain detection."""
import requests

import shared


PARKED_WORDS = (
    'domain',
    'redirect',
    'for sale',
    'purchase',
    'registrar',
    'hosted',
)

CONTENT_MAX = 1024 * 100


def _domain_redirects(domain, path=''):
    """Returns whether a domain (and optional path) redirects to another."""
    req = requests.get(
        'http://{}/{}'.format(domain, path),
        **shared.REQ_KWARGS
    )
    landed_domain = shared.get_domain(req.url)
    return landed_domain != domain, landed_domain, req.content[:CONTENT_MAX]


def get_text(score):
    """Returns a textual representation of the likelihood that a domain is
    parked, based on the score.
    """
    if score == 0:
        return 'Unlikely'
    elif score <= 0.3:
        return 'Possibly'
    elif score <= 0.6:
        return 'Fairly likely'
    elif score <= 0.85:
        return 'Quite likely'
    else:
        return 'Highly likely'


def get_score(domain):
    """Takes a punt as to whether a domain is parked or not.

    Returns a score between 0 and 1 as to the likelihood that the domain is
    parked. 1 = highly likely.

    TODO: make less susceptible to 'www.' redirects on naked domains.
    """
    score = 0

    try:
        redirects, landed_domain1, content = _domain_redirects(domain)
        if redirects:
            score += 1
    except requests.ConnectionError:
        return 0

    try:
        redirects, landed_domain2, _ = _domain_redirects(
            domain, 'dnstwister_parked_check'
        )
    except requests.ConnectionError:
        return 0

    if redirects:
        score += 1

    if landed_domain1 == landed_domain2:
        score += 1

    word_score = 0
    for word in PARKED_WORDS:
        if word.lower() in content.lower():
            word_score += 1.0
    score += (word_score / len(PARKED_WORDS)) * 3

    return round(score / 6.0, 2)
