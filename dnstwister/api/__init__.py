"""The analysis API endpoint."""
import binascii
import flask
import urlparse

import checks.parked as parked
import dnstwister.tools as tools

app = flask.Blueprint('api', __name__)


ENDPOINTS = ('parked_score', 'resolve_ip', 'fuzz')


@app.route('/')
def api_definition():
    """API definition."""
    return flask.jsonify({
        'url': flask.request.base_url,
        'domain_fuzzer_url': tools.api_url(fuzz, 'domain_as_hex'),
        'parked_check_url': tools.api_url(parked_score, 'domain_as_hex'),
        'ip_resolution_url': tools.api_url(resolve_ip, 'domain_as_hex'),
    })


def standard_api_values(domain, skip=''):
    """Return the set of key-value pairs for the api inter-relationships."""
    payload = {}
    hexdomain = binascii.hexlify(domain)
    for endpoint in ENDPOINTS:
        if endpoint == skip:
            continue
        key = '{}_url'.format(endpoint)
        view_path = '.{}'.format(endpoint)
        path = flask.url_for(view_path, hexdomain=hexdomain)
        url = urlparse.urljoin(flask.request.url_root, path)
        payload[key] = url

    if skip != 'url':
        payload['url'] = flask.request.base_url

    if skip != 'domain':
        payload['domain'] = domain

    if skip != 'hex_repr':
        payload['hex_repr'] = hexdomain

    return payload


@app.route('/parked/<hexdomain>')
def parked_score(hexdomain):
    """Calculates "parked" scores from 0-1."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )
    payload = standard_api_values(domain, skip='parked_score')
    payload['score'] = parked.get_score(domain)
    return flask.jsonify(payload)


@app.route('/ip/<hexdomain>')
def resolve_ip(hexdomain):
    """Resolves Domains to IPs."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    ip, error = tools.resolve(domain)

    payload = standard_api_values(domain, skip='resolve_ip')
    payload['ip'] = ip
    payload['error'] = error
    return flask.jsonify(payload)


@app.route('/fuzz/<hexdomain>')
def fuzz(hexdomain):
    """Calculates the dnstwist "fuzzy domains" for a domain."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    fuzz_result = tools.fuzzy_domains(domain)
    fuzz_payload = []
    for result in fuzz_result:
        result_payload = standard_api_values(result['domain-name'], skip='url')
        result_payload['fuzzer'] = result['fuzzer']
        fuzz_payload.append(result_payload)

    payload = standard_api_values(domain, skip='fuzz')
    payload['fuzzy_domains'] = fuzz_payload
    return flask.jsonify(payload)
