"""Generic tools."""
import binascii
import os
import re
import random
import socket
import urllib.parse

import dns.resolver
import flask

from dnstwister.tools import tld_db
import dnstwister.dnstwist as dnstwist
from dnstwister.core.domain import Domain


RESOLVER = dns.resolver.Resolver()
RESOLVER.lifetime = 0.5
RESOLVER.timeout = 0.5


def try_parse_domain_from_hex(hex_encoded_ascii_domain):
    try:
        ascii_domain_text = bytes.fromhex(hex_encoded_ascii_domain).decode('ascii')
    except (ValueError, TypeError):
        return

    return Domain.try_parse(ascii_domain_text)


def fuzzy_domains(domain):
    """Return the fuzzy domains."""
    fuzzer = dnstwist.DomainFuzzer(domain.to_unicode())
    fuzzer.fuzz()
    return list(fuzzer.domains)


def analyse(domain):
    """Analyse a domain."""
    data = {'fuzzy_domains': []}
    results = fuzzy_domains(domain)

    # Add a hex-encoded version of the domain for the later IP resolution. We
    # do this because the same people who may use this app already have
    # blocking on things like www.exampl0e.com in URLs...
    for result in results:
        result['hex'] = Domain(result['domain-name']).to_hex()
    data['fuzzy_domains'] = results

    return (domain, data)


def clean_up_search_term(search_term):
    """Remove HTTP(s) schemes and trailing slashes."""
    search_term = re.sub('(^http(s)?://)|(/$)', '', search_term, re.IGNORECASE)

    return Domain.try_parse(search_term)


def suggest_domain(search_domain):
    """Suggest a domain based on the search fields."""

    search_terms = search_domain.split(' ')

    # Check for a simple common typo first - putting comma instead of period
    # in-between the second- and top-level domains.
    if len(search_terms) == 1:
        candidate = re.sub(r'[,/-]', '.', search_terms[0])
        if Domain.try_parse(candidate) is not None:
            return candidate

    # Pick up space-separated domain levels.
    if len(search_terms) == 2 and search_terms[1] in tld_db.TLDS:
        candidate = '.'.join(search_terms)
        if Domain.try_parse(candidate) is not None:
            return candidate

    # Attempt to make a domain from the terms.
    joiners = ('', '-')  # for now, also trialling ('', '-', '.')
    tlds = ('com',)  # for now
    suggestions = []

    # Filter out a ton of garbage being submitted
    if len(search_terms) > 2:
        return

    # Filter out long words
    search_terms = [term
                    for term
                    in search_terms
                    if len(term) < 30]

    # Filter out silly characters
    search_terms = [re.sub(r'[^a-zA-Z0-9\-]', '', term)
                    for term
                    in search_terms]

    # Join the terms
    for joiner in joiners:
        suggestions.append(joiner.join(search_terms))

    # Add TLDs
    suggested_domains = []
    for tld in tlds:
        suggested_domains.extend(['{}.{}'.format(s.lower(), tld)
                                  for s
                                  in suggestions])

    # Drop out duplicates
    suggested_domains = list(set(suggested_domains))

    # Filter for those that are actually valid domains
    valid_suggestions = list(filter(
        lambda d: Domain.try_parse(d) is not None, suggested_domains
    ))

    if len(valid_suggestions) == 0:
        return

    return random.choice(valid_suggestions)


def resolve(domain):
    """Resolves a domain to an IP.

    Returns and (IP, False) on successful resolution, (False, False) on
    successful failure to resolve and (None, True) on error in attempting to
    resolve.
    """
    idna_domain = domain.to_ascii()

    # Try for an 'A' record.
    try:
        ip_addr = str(sorted(RESOLVER.query(idna_domain, 'A'))[0].address)

        # Weird edge case that sometimes happens?!?!
        if ip_addr != '127.0.0.1':
            return ip_addr, False
    except:
        pass

    # Try for a simple resolution if the 'A' record request failed
    try:
        ip_addr = socket.gethostbyname(idna_domain)

        # Weird edge case that sometimes happens?!?!
        if ip_addr != '127.0.0.1':
            return ip_addr, False
    except socket.gaierror:
        # Indicates failure to resolve to IP address, not an error in
        # the attempt.
        return False, False
    except:
        pass

    # Error due to exception or 127.0.0.1 issue.
    return False, True


def random_id(n_bytes=32):
    """Generate a random id for an email subscription (for instance)."""
    return binascii.hexlify(os.urandom(n_bytes)).decode('ascii')


def api_url(view, var_pretty_name):
    """Create nice API urls with place holders."""
    view_path = '.{}'.format(view.__name__)
    route_var = view.__code__.co_varnames[:view.__code__.co_argcount][0]
    path = flask.url_for(view_path, **{route_var: ''})
    path += '{' + var_pretty_name + '}'
    return urllib.parse.urljoin(
        flask.request.url_root,
        path
    )
