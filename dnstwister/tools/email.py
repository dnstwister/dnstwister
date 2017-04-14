"""Email tools."""
import binascii
import jinja2


TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader('dnstwister', 'templates')
)


def domain_format(domain):
    """Given a domain in plain text format, render it in a manner that will
    prevent auto-linking/interception in an email.

    Testing suggests the span wrapping is the best so far.
    """
    domain = domain.replace('.', '<span>.</span>')
    return domain


def analysis_url(domain):
    """Format a domain as an analysis link."""
    return 'https://dnstwister.report/analyse/{}'.format(binascii.hexlify(domain))



TEMPLATES.filters['domain_format'] = domain_format
TEMPLATES.filters['analysis_url'] = analysis_url


def render_email(template, **kwargs):
    """Render an email body."""
    template = TEMPLATES.get_template('email/{}'.format(template))
    return template.render(**kwargs)
