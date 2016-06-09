"""The dnstwist API endpoint."""
import binascii
import flask
import urlparse

import dnstwister.tools as tools

app = flask.Blueprint('dnstwist_api', __name__)


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
        'domain_fuzzer_url': api_url(fuzzy_domains, 'domain_as_hex'),
    })


@app.route('/fuzz/<hexdomain>')
def fuzzy_domains(hexdomain):
    """Calculates the dnstwist "fuzzy domains" for a domain."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    fuzz_result = tools.fuzzy_domains(domain)
    payload = []
    for result in fuzz_result:
        hex_repr = binascii.hexlify(result['domain-name'])
        fuzz_url = urlparse.urljoin(
            flask.request.url_root, flask.url_for(
                '.fuzzy_domains', hexdomain=hex_repr
            )
        )
        payload.append({
            'domain': result['domain-name'],
            'fuzzer': result['fuzzer'],
            'hex_repr': hex_repr,
            'fuzz_url': fuzz_url,
        })

    return flask.jsonify({
        'url': flask.request.base_url,
        'domain': domain,
        'fuzzy_domains': payload,
    })
