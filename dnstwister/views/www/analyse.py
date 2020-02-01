"""Domain analysis page."""
import flask

from dnstwister import app
import dnstwister.tools as tools
from dnstwister.core.domain import Domain


@app.route('/analyse/<hexdomain>')
def analyse(hexdomain):
    """Do a domain analysis."""
    domain = tools.try_parse_domain_from_hex(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    return flask.render_template(
        'www/analyse.html',
        domain=domain,
        hexdomain=hexdomain,
    )
