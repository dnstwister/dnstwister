"""Test the Google Public DNS fallback"""
import socket

from dnstwister import tools


def _is_valid_ip(ip_string):
    """Throws socket.error if not a valid IP address."""
    socket.inet_aton(ip_string)
    return True


def test_failed_domain():
    """Test Google Public DNS on a failing domain."""
    domain = 'thisdomainisgoingtofaileimprettysure.com'
    ip_addr, error = tools.google_resolve(domain)

    assert not ip_addr
    assert not error


def test_successful_domain():
    """Test Google Public DNS on a working domain."""
    domain = 'dnstwister.report'
    ip_addr, error = tools.google_resolve(domain)

    assert _is_valid_ip(ip_addr)
    assert not error


def test_successful_unicode_domain():
    """Check Google's happy with Unicode."""
    domain = u'\x94sterreich.icom.museum'
    ip_addr, error = tools.google_resolve(domain)

    assert _is_valid_ip(ip_addr)
    assert not error


def test_failure_to_resolve(f_httpretty):
    """Bringing in httpretty breaks requests, this is intentional for this
    test.
    """
    domain = 'dnstwister.report'
    ip_addr, error = tools.google_resolve(domain)

    assert not ip_addr
    assert error
