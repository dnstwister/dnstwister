"""The analysis API endpoint."""
import binascii
import urlparse
import whois as whois_mod

import flask
from flask import current_app

from dnstwister.api.checks import parked
from dnstwister.api.checks import safebrowsing
from dnstwister import tools


app = flask.Blueprint('api', __name__)


ENDPOINTS = ('parked_score', 'resolve_ip', 'fuzz')


@app.route('/')
def api_definition():
    """API definition."""
    return flask.jsonify({
        'url': flask.request.base_url,
        'domain_to_hexadecimal_url': tools.api_url(domain_to_hex, 'domain'),
        'domain_fuzzer_url': tools.api_url(fuzz, 'domain_as_hexadecimal'),
        'parked_check_url': tools.api_url(parked_score, 'domain_as_hexadecimal'),
        'google_safe_browsing_url': tools.api_url(safebrowsing_check, 'domain_as_hexadecimal'),
        'ip_resolution_url': tools.api_url(resolve_ip, 'domain_as_hexadecimal'),
        'whois_url': tools.api_url(whois, 'domain_as_hexadecimal'),
    })


def standard_api_values(domain, skip=''):
    """Return the set of key-value pairs for the api inter-relationships."""
    payload = {}
    hexdomain = tools.encode_domain(domain)
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

    if skip != 'domain_as_hexadecimal':
        payload['domain_as_hexadecimal'] = hexdomain

    return payload


@app.route('/whois/<hexdomain>')
def whois(hexdomain):
    """Returns whois information."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )
    payload = standard_api_values(domain, skip='whois')
    try:
        payload['whois_text'] = whois_mod.whois(domain).text.strip()
        if payload['whois_text'] == '':
            raise Exception('No whois data retrieved')
    except Exception as ex:
        current_app.logger.error(
            'Unable to retrieve whois info for domain: {}'.format(ex)
        )
        flask.abort(500, 'Unable to retrieve whois info')

    return flask.jsonify(payload)


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
    score, score_text, redirects, dressed, dest = parked.get_score(domain)
    payload['score'] = score
    payload['score_text'] = score_text
    payload['redirects'] = redirects
    payload['redirects_to'] = dest
    payload['dressed'] = dressed
    return flask.jsonify(payload)


@app.route('/safebrowsing/<hexdomain>')
def safebrowsing_check(hexdomain):
    """Returns number of hits in Google Safe Browsing."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )
    payload = standard_api_values(domain, skip='safebrowsing')
    payload['issue_detected'] = safebrowsing.get_report(domain) != 0
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

    ip_addr, error = tools.resolve(domain)

    payload = standard_api_values(domain, skip='resolve_ip')
    payload['ip'] = ip_addr
    payload['error'] = error
    return flask.jsonify(payload)


@app.route('/to_hex/<domain>')
def domain_to_hex(domain):
    """Helps you convert domains to hex."""
    hexdomain = tools.encode_domain(domain)
    if tools.parse_domain(hexdomain) is None:
        flask.abort(400, 'Malformed domain.')

    payload = standard_api_values(domain, skip='domain_to_hex')
    payload['domain_as_hexadecimal'] = hexdomain
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
