"""Generic tools."""
import binascii
import os
import re
import random
import socket
import string
import urlparse

import dns.resolver
import flask
import requests

from dnstwister import app
from dnstwister import cache
from dnstwister.tools import tld_db
import dnstwister.dnstwist as dnstwist


RESOLVER = dns.resolver.Resolver()
RESOLVER.lifetime = 0.1
RESOLVER.timeout = 0.1

GOOGLEDNS = 'https://dns.google.com/resolve?name={}'
GOOGLEDNS_SUCCESS = 0
GOOGLEDNS_A_RECORD = 1


def encode_domain(domain):
    """Given a domain with possible Unicode chars, encode it to hex."""
    try:
        return binascii.hexlify(domain.encode('idna'))
    except UnicodeError:
        # Some strange invalid Unicode domains
        return None


def decode_domain(encoded_domain):
    """Return a domain from hex."""
    return binascii.unhexlify(encoded_domain).decode('idna')


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
        result['hex'] = encode_domain(result['domain-name'])
    data['fuzzy_domains'] = results

    return (domain, data)


def parse_post_data(post_data):
    """Parse post data to return a domain."""

    # Remove HTTP(s) schemes and trailing slashes.
    domain = re.sub('(^http(s)?://)|(/$)', '', post_data, re.IGNORECASE)

    # Parse through the normal process.
    return parse_domain(domain.strip())


def parse_domain(encoded_domain):
    """Given a hex-encoded string, try to decode and validate it and if it is
    a valid domain, return it.

    Return None on un-decodable or invalid domain.
    """
    try:
        decoded_domain = decode_domain(encoded_domain)
        if dnstwist.validate_domain(decoded_domain):
            return decoded_domain.lower()
    except:
        pass


def suggest_domain(search_domain):
    """Suggest a domain based on the search fields."""

    search_terms = search_domain.split(' ')

    # Check for a simple common typo first - putting comma instead of period
    # in-between the second- and top-level domains.
    if len(search_terms) == 1:
        candidate = re.sub(r'[,/-]', '.', search_terms[0])
        if dnstwist.validate_domain(candidate):
            return candidate

    # Pick up space-separated domain levels.
    if len(search_terms) == 2 and search_terms[1] in tld_db.TLDS:
        candidate = '.'.join(search_terms)
        if dnstwist.validate_domain(candidate):
            return candidate

    # Attempt to make a domain from the terms.
    joiners = ('', '-') # for now, also trialling ('', '-', '.')
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
    valid_suggestions = filter(
        dnstwist.validate_domain, suggested_domains
    )

    if len(valid_suggestions) == 0:
        return

    return random.choice(valid_suggestions)


def is_valid_ip(ip_string):
    """Matches valid ipv4 IP addresses."""
    try:
        socket.inet_aton(ip_string)
        return True
    except socket.error:
        return False


@cache.memoize(3600)
def resolve(domain):
    """Resolves a domain to an IP.

    Returns and (IP, False) on successful resolution, (False, False) on
    successful failure to resolve and (None, True) on error in attempting to
    resolve.

    Cached to 1 hour.
    """
    if dnstwist.validate_domain(domain) is None:
        return False, True

    idna_domain = domain.encode('idna')

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
    except:
        pass

    return google_resolve(domain)


def google_resolve(domain):
    """Google's Public DNS resolver."""
    try:
        idna_domain = domain.encode('idna')
        response = requests.get(GOOGLEDNS.format(idna_domain)).json()
        if response['Status'] == GOOGLEDNS_SUCCESS:
            if 'Answer' in response.keys():
                answer = response['Answer'][0]
                if answer['type'] == GOOGLEDNS_A_RECORD:
                    ip_addr = answer['data']
                    if is_valid_ip(ip_addr):
                        return ip_addr, False
        return False, False
    except Exception as ex:
        app.logger.error(
            'Failed to resolve IP via Google Public DNS: {}'.format(ex)
        )
        return False, True


def random_id(n_bytes=32):
    """Generate a random id for an email subscription (for instance)."""
    return binascii.hexlify(os.urandom(n_bytes))


def api_url(view, var_pretty_name):
    """Create nice API urls with place holders."""
    view_path = '.{}'.format(view.func_name)
    route_var = view.func_code.co_varnames[:view.func_code.co_argcount][0]
    path = flask.url_for(view_path, **{route_var: ''})
    path += '{' + var_pretty_name + '}'
    return urlparse.urljoin(
        flask.request.url_root,
        path
    )


def domain_renderer(domain):
    """Add IDNA values beside Unicode domains."""
    idna_domain = domain.encode('idna')
    if idna_domain == domain:
        return domain

    return domain + ' ({})'.format(idna_domain)
