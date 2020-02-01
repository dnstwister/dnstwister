"""Shared helpers and settings for the analysis API."""
import urllib.parse

from dnstwister.core.domain import Domain


_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'

_CLIENT_HEADERS = {
    'User-Agent': _USER_AGENT,
}

REQ_KWARGS = {
    'headers': _CLIENT_HEADERS,
    'timeout': 5,  # seconds
}


def get_domain(url):
    """Return the domain from a URL."""
    return Domain.try_parse(urllib.parse.urlparse(url).netloc.split(':')[0])
