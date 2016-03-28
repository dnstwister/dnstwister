"""API page."""
import flask

from dnstwister import app
import dnstwister.tools as tools


@app.route('/ip/<hexdomain>')
def resolve(hexdomain):
    """Resolves Domains to IPs."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    ip, error = tools.resolve(domain)

    # Response IP is now an IP address, or False.
    return flask.json.jsonify({'ip': ip, 'error': error})
