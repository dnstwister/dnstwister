"""Parked domain detection."""
import requests

import dnstwister.tools.tld_db as tld_db
from dnstwister.api.checks import shared

PARKED_WORDS = (
    'domain',
    'redirect',
    'for sale',
    'purchase',
    'registrar',
    'hosted',
    'buy this',
    'buy this domain',
    'domain names',
    'domain names for sale',
)

# In-browser redirect checks
REDIRECT_HINTS = (
    '.location',
    'redirect',
    'fwd',
    'url=',
    'forward',
    'refresh',
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


def second_level(domain):
    """Return the second-level bit of a domain.

    Determine tld by finding the longest tld that is the end of the passed in
    domain.
    """
    candidate = ''
    for tld in tld_db.TLDS:
        if domain.endswith('.' + tld) and len(tld) > len(candidate):
            candidate = tld

    if candidate != '':
        return domain.rsplit('.' + candidate, 1)[0].split('.')[-1]
    return ''


def dressed(domain, redirected_domain):
    """Returns whether the domain's second-level is the same.

    For example:

        example.com -> www.example.com
    """
    return (
        (domain != redirected_domain)
        and
        (second_level(domain) == second_level(redirected_domain))
    )


def soft_redirects(content, threshold=0):
    """Tries to guess if a page redirects in-browser."""
    count = 0
    for hint in REDIRECT_HINTS:
        if hint in content.lower():
            count += 1
    return count > threshold


def get_score(domain):
    """Takes a punt as to whether a domain is parked or not.

    Returns a score between 0 and 1 as to the likelihood that the domain is
    parked. 1 = highly likely.
    """
    score = 0

    try:
        redirects_domain, landed_domain1, content = _domain_redirects(domain)
        if redirects_domain:
            if not dressed(domain, landed_domain1):
                score += 1
    except:
        redirects_domain = False
        landed_domain1 = ''
        content = ''

    if soft_redirects(content):
        score += 1

    try:
        redirects_paths, landed_domain2, _ = _domain_redirects(
            domain, 'dnstwister_parked_check'
        )
    except:
        redirects_paths = False
        landed_domain2 = ''

    if redirects_paths:
        if not dressed(domain, landed_domain2):
            score += 1

    if landed_domain1 == landed_domain2 and redirects_paths:
        score += 1

    word_score = 0
    for word in PARKED_WORDS:
        if word.lower() in content.lower():
            word_score += 1.0
    score += (word_score / len(PARKED_WORDS)) * 5

    normalised_score = round(score / 7.0, 2)

    normalised_score = min(1, normalised_score)

    return (
        normalised_score,
        get_text(normalised_score),
        redirects_domain,
        redirects_domain and dressed(domain, landed_domain1),
        landed_domain1 if redirects_domain else None,
    )
