"""Tools specific to template rendering."""
import dnstwister.tools
from dnstwister.core.domain import Domain


def domain_renderer(domain):
    """Template helper to add IDNA values beside Unicode domains."""
    return str(Domain(domain))


def domain_encoder(domain):
    """Template helper to encode domains for URLs."""
    return Domain(domain).to_hex()
