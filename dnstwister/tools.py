""" Non-GAE tools.
"""
import base64
import dnstwist
import operator


def parse_domain(get_dict):
    """ Given the dict of key:value pairs from a GET request, parse the 'b64'
        key and confirm it's a valid domain. If anything goes wrong, just
        return None.
    """
    try:
        domainb64 = get_dict['b64']
    except KeyError:
        return

    try:
        domain = base64.b64decode(domainb64)
    except TypeError:
        return

    if not dnstwist.validate_domain(domain):
        return

    return domain


def query_domains(data_dict):
    """ Return the queried domains from a request data dict, or None.

        Domains are newline separated in a textarea.
    """
    try:
        domains = data_dict['domains']
    except KeyError:
        return

    domains = filter(
        None, map(operator.methodcaller('strip'), domains.split('\n'))
    )

    return list(set(domains)) if len(domains) > 0 else None
