"""Email tools."""
import jinja2

import dnstwister.tools.template as template_tools


TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader('dnstwister', 'templates')
)


def domain_renderer(domain):
    """Given a domain in plain text format, render it in a manner that will
    prevent auto-linking/interception in an email.

    Testing suggests the span wrapping is the best so far.
    """
    domain = template_tools.domain_renderer(domain)
    domain = domain.replace('.', '<span>.</span>')
    return domain


TEMPLATES.filters['domain_renderer'] = domain_renderer


def render_email(template, **kwargs):
    """Render an email body."""
    template = TEMPLATES.get_template('email/{}'.format(template))
    return template.render(**kwargs)
