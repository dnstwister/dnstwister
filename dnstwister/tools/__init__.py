""" Non-GAE tools.
"""
import base64
import binascii
import dns.resolver
import operator
import os
import re
import socket
import string

from dnstwister import cache
import dnstwister.dnstwist as dnstwist
import dnstwister.whois as whois


RESOLVER = dns.resolver.Resolver()
RESOLVER.lifetime = 0.1
RESOLVER.timeout = 0.1


def analyse(domain):
    """Analyse a domain."""
    data = {'fuzzy_domains': []}
    fuzzer = dnstwist.DomainFuzzer(domain)
    fuzzer.fuzz()
    results = list(fuzzer.domains)

    if len(results) == 0:
        return None

    # Add a hex-encoded version of the domain for the later IP resolution. We
    # do this because the same people who may use this app already have
    # blocking on things like www.exampl0e.com in URLs...
    for r in results:
        r['hex'] = binascii.hexlify(r['domain-name'])
    data['fuzzy_domains'] = results

    return (domain, data)


def parse_domain(hexdomain):
    """Given a hex-encoded string (hopefully), return a valid domain.

    Try to handle old-style base64 domains.

    Return None on invalid domain/data.
    """
    try:
        domain = binascii.unhexlify(hexdomain)
    except TypeError:
        try:
            # Old style URLs
            domain = base64.b64decode(hexdomain)
        except TypeError:
            return

    if not dnstwist.validate_domain(domain):
        return

    return domain


def query_domains(data_dict):
    """ Return the valid queried domains from a request data dict, or None.

        Domains are newline separated in a textarea.
    """
    try:
        domains = data_dict['domains']
    except KeyError:
        return

    domains = re.sub(r'[\t\r, ]', '\n', domains)

    # Filter out blank lines, leading/trailing whitespace
    domains = filter(
        None, map(string.strip, domains.split('\n'))
    )

    # Remove HTTP(s) schemes and trailing slashes.
    domains = [re.sub('(^http(s)?://)|(/$)', '', domain, re.IGNORECASE)
               for domain
               in domains]

    # Strip leading/trailing whitespace again.
    domains = filter(None, map(string.strip, domains))

    # Filter for only valid domains
    domains = filter(
        dnstwist.validate_domain, domains
    )

    return sorted(list(set(domains))) if len(domains) > 0 else None


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


def whois_query(domain):
    """Returns the whois info for a domain or None."""
    try:
        return whois.lookup(domain)
    except:
        return 'Error: whois lookup failed'


def random_id(n_bytes=32):
    """Generate a random id for an email subscription (for instance)."""
    return binascii.hexlify(os.urandom(n_bytes))
