"""Email tools."""
import jinja2


TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader('dnstwister', 'templates')
)

def domain_format(domain):
    """Given a domain in plain text format, render it in a manner that will
    prevent auto-linking/interception in an email.
    """
#    domain = domain.replace('.', ' . ')
    domain = domain.replace('.', '<span>.</span>')
    return domain

TEMPLATES.filters['domain_format'] = domain_format

def render_email(template, **kwargs):
    """Render an email body."""
    template = TEMPLATES.get_template('email/{}'.format(template))
    return template.render(**kwargs)
