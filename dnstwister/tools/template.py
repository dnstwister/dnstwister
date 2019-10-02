"""Tools specific to template rendering."""


def domain_renderer(domain):
    """Template helper to add IDNA values beside Unicode domains."""
    idna_domain = domain.encode('idna')
    if idna_domain == domain:
        return domain

    return domain + ' ({})'.format(idna_domain)
