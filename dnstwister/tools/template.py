"""Tools specific to template rendering."""
import dnstwister.tools


def domain_renderer(domain):
    """Template helper to add IDNA values beside Unicode domains."""
    idna_domain = domain.encode('idna')
    if idna_domain == domain:
        return domain

    return domain + ' ({})'.format(idna_domain)


def domain_encoder(domain):
    """Template helper to encode domains for URLs."""
    return dnstwister.tools.encode_domain(domain)
