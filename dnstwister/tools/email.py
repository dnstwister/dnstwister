"""Email tools."""
import jinja2


TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader('dnstwister', 'templates')
)


def render_email(template, **kwargs):
    """Render an email body."""
    template = TEMPLATES.get_template('email/{}'.format(template))
    return template.render(**kwargs)
