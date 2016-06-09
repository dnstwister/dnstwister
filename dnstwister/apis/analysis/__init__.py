"""The analysis API endpoint."""
import flask
import urlparse

import checks.parked as parked
import dnstwister.tools as tools

app = flask.Blueprint('analysis_api', __name__)


def api_url(view, var_pretty_name):
    """Create nice API urls."""
    view_path = '.{}'.format(view.func_name)
    route_var = view.func_code.co_varnames[:view.func_code.co_argcount][0]
    path = flask.url_for(view_path, **{route_var: ''})
    path += '{' + var_pretty_name + '}'
    return urlparse.urljoin(
        flask.request.url_root,
        path
    )


@app.route('/')
def api_definition():
    """API definition."""
    return flask.jsonify({
        'url': flask.request.base_url,
        'parked_check_url': api_url(parked_score, 'domain_as_hex'),
        'ip_resolution_url': api_url(ip, 'domain_as_hex'),
    })


@app.route('/parked/<hexdomain>')
def parked_score(hexdomain):
    """Calculates "parked" scores from 0-1."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )
    return flask.jsonify({
        'url': flask.request.base_url,
        'domain': domain,
        'score': parked.get_score(domain),
    })


@app.route('/ip/<hexdomain>')
def ip(hexdomain):
    """Resolves Domains to IPs."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    ip, error = tools.resolve(domain)

    # Response IP is now an IP address, or False.
    return flask.jsonify({
        'url': flask.request.base_url,
        'domain': domain,
        'ip': ip,
        'error': error,
    })
