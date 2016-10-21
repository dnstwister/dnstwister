""" Generic tools.
"""
import base64
import binascii
import os
import re
import random
import socket
import string
import urlparse

import dns.resolver
import flask

from dnstwister import cache
import dnstwister.dnstwist as dnstwist


RESOLVER = dns.resolver.Resolver()
RESOLVER.lifetime = 0.1
RESOLVER.timeout = 0.1


def fuzzy_domains(domain):
    """Return the fuzzy domains."""
    fuzzer = dnstwist.DomainFuzzer(domain)
    fuzzer.fuzz()
    return list(fuzzer.domains)


def analyse(domain):
    """Analyse a domain."""
    data = {'fuzzy_domains': []}
    results = fuzzy_domains(domain)

    if len(results) == 0:
        return None

    # Add a hex-encoded version of the domain for the later IP resolution. We
    # do this because the same people who may use this app already have
    # blocking on things like www.exampl0e.com in URLs...
    for result in results:
        result['hex'] = binascii.hexlify(result['domain-name'])
    data['fuzzy_domains'] = results

    return (domain, data)


def parse_post_data(post_data):
    """Parse post data to return a set of domain candidates."""
    data = re.sub(r'[\t\r, ]', '\n', post_data)

    # Filter out blank lines, leading/trailing whitespace
    data = filter(
        None, map(string.strip, data.split('\n'))
    )

    # Remove HTTP(s) schemes and trailing slashes.
    data = [re.sub('(^http(s)?://)|(/$)', '', domain, re.IGNORECASE)
            for domain
            in data]

    # Strip leading/trailing whitespace again.
    data = filter(None, map(string.strip, data))

    # Make all lower-case
    data = map(string.lower, data)

    return sorted(list(set(data)))


def parse_domain(encoded_domain):
    """Given a plain, b64- or hex-encoded string, try to validate it and if
    it is valid, return it.

    Return None on un-decodable or invalid domain.
    """

    # If it's a valid plain-text domain, return it
    try:
        if dnstwist.validate_domain(encoded_domain):
            return encoded_domain
    except:
        pass

    # If it is hex or base64 encoded, decode it.
    try:
        domain = binascii.unhexlify(encoded_domain)
    except TypeError:
        try:
            # Old style URLs
            domain = base64.b64decode(encoded_domain)
        except TypeError:
            return

    # If the decoded domain is valid, return it
    try:
        if dnstwist.validate_domain(domain):
            return domain.lower()
    except:
        pass


def suggest_domain(seach_terms):
    """Suggest a domain based on the search fields."""
    joiners = ('-', '.')
    tlds = ('com',)  # for now
    suggestions = []

    # Filter out a ton of garbage being submitted
    if len(seach_terms) > 2:
        return []

    # Filter out long words
    seach_terms = [term
                   for term
                   in seach_terms
                   if len(term) < 30]

    # Filter out silly characters
    seach_terms = [re.sub(r'[^a-zA-Z0-9\-]', '', term)
                   for term
                   in seach_terms]

    # Join the terms
    for joiner in joiners:
        suggestions.append(joiner.join(seach_terms))

    # Attempt to form an acronym
    if len(seach_terms) > 1:
        acronym = ''
        for term in seach_terms:
            if len(term) <= 2:
                acronym += term
            else:
                acronym += term[0]
        suggestions.append(acronym)

    # Add TLDs
    suggested_domains = []
    for tld in tlds:
        suggested_domains.extend(['{}.{}'.format(s.lower(), tld)
                                  for s
                                  in suggestions])

    # Drop out duplicates
    suggested_domains = list(set(suggested_domains))

    # Filter for those that are actually valid domains
    valid_suggestions = filter(
        dnstwist.validate_domain, suggested_domains
    )

    if len(valid_suggestions) == 0:
        return

    return random.choice(valid_suggestions)


@cache.memoize(3600)
def resolve(domain):
    """Resolves a domain to an IP.

    Returns and (IP, False) on successful resolution, (False, False) on
    successful failure to resolve and (None, True) on error in attempting to
    resolve.

    Cached to 1 hour.
    """
    # Try for an 'A' record.
    try:
        ip = str(sorted(RESOLVER.query(domain, 'A'))[0].address)
        return ip, False
    except:
        pass

    # Try for a simple resolution if the 'A' record request failed
    try:
        ip = socket.gethostbyname(domain)
        return ip, False
    except socket.gaierror:
        # Indicates failure to resolve to IP address, not an error in
        # the attempt.
        return False, False
    except:
        return False, True


def random_id(n_bytes=32):
    """Generate a random id for an email subscription (for instance)."""
    return binascii.hexlify(os.urandom(n_bytes))


def api_url(view, var_pretty_name):
    """Create nice API urls with placeholders."""
    view_path = '.{}'.format(view.func_name)
    route_var = view.func_code.co_varnames[:view.func_code.co_argcount][0]
    path = flask.url_for(view_path, **{route_var: ''})
    path += '{' + var_pretty_name + '}'
    return urlparse.urljoin(
        flask.request.url_root,
        path
    )
