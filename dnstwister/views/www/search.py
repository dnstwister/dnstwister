"""Search/report page."""
import binascii
import concurrent.futures
import json

import flask

from dnstwister import app
import dnstwister.tools as tools
from dnstwister.core.domain import Domain


def html_render(domain):
    """Render and return the html report."""
    return flask.render_template(
        'www/report.html',
        domain=domain,
        report=tools.analyse(domain)[1],
        exports={'json': 'json', 'csv': 'csv'}
    )


def json_render(domain):
    """Render and return the json-formatted report."""
    json_filename = 'dnstwister_report_{}.json'.format(domain.to_ascii())

    def local_resolve_candidate(candidate):
        domain = Domain(candidate['domain-name'])
        ip_addr, error = tools.resolve(domain)
        return candidate['fuzzer'], domain, ip_addr, error

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = executor.map(
            local_resolve_candidate,
            tools.analyse(domain)[1]['fuzzy_domains']
        )

    results = []
    for (fuzzer, entry_domain, ip_addr, error) in futures:
        results.append({
            'domain-name': entry_domain.to_ascii(),
            'fuzzer': fuzzer,
            'hex': entry_domain.to_hex(),
            'resolution': {
                'error': error,
                'ip': ip_addr
            }
        })

    response = {
        domain.to_ascii(): {
            'fuzzy_domains': results
        }
    }

    return flask.Response(
        json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')),
        headers={
            'Content-Disposition': 'attachment; filename=' + json_filename
        },
        content_type='application/json'
    )


def csv_render(domain):
    """Render and return the csv-formatted report."""
    headers = ('Domain', 'Type', 'Tweak', 'IP', 'Error')
    csv_filename = 'dnstwister_report_{}.csv'.format(domain.to_ascii())

    def local_resolve_candidate(candidate):
        domain = Domain(candidate['domain-name'])
        ip_addr, error = tools.resolve(domain)
        return candidate['fuzzer'], domain, ip_addr, error

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = executor.map(
            local_resolve_candidate,
            tools.analyse(domain)[1]['fuzzy_domains']
        )

    csv = ','.join(headers) + '\n'
    for (fuzzer, entry_domain, ip_addr, error) in futures:
        row = (
            domain.to_ascii(),
            fuzzer,
            entry_domain.to_ascii(),
            str(ip_addr),
            str(error),
        )
        csv += ','.join(row) + '\n'

    return flask.Response(
        csv,
        headers={
            'Content-Disposition': 'attachment; filename=' + csv_filename
        },
        mimetype='text/csv',
    )


@app.route('/search', methods=['POST'])
def search_post():
    """Handle form submit."""
    try:
        post_data = flask.request.form['domains']
    except KeyError:
        app.logger.info(
            'Missing "domains" key from POST: {}'.format(flask.request.form)
        )
        return flask.redirect('/error/2')

    if post_data is None or post_data.strip() == '':
        app.logger.info(
            'No data in "domains" key in POST'
        )
        return flask.redirect('/error/2')

    searched_domain = Domain.try_parse(post_data.strip())

    if searched_domain is None:
        return handle_invalid_domain(binascii.hexlify(post_data.encode()).decode('ascii'))

    return flask.redirect('/search/{}'.format(searched_domain.to_hex()))


def handle_invalid_domain(search_term_as_hex):
    """Called when no valid domain found in GET param, creates a suggestion
    to return to the user.
    """
    decoded_search = None
    try:
        decoded_search = bytes.fromhex(search_term_as_hex).decode('ascii')
    except:
        pass

    if decoded_search is not None:
        suggestion = tools.suggest_domain(decoded_search)
        if suggestion is not None:
            app.logger.info(
                'Not a valid domain in GET: {}, suggesting: {}'.format(
                    search_term_as_hex, suggestion
                )
            )
            return flask.redirect(
                '/error/0?suggestion={}'.format(Domain(suggestion).to_hex())
            )

    app.logger.info(
        'Not a valid domain in GET: {}'.format(search_term_as_hex)
    )
    return flask.redirect('/error/0')


@app.route('/search/<search_domain>')
@app.route('/search/<search_domain>/<fmt>')
def search(search_domain, fmt=None):
    """Handle redirect from form submit."""
    domain = tools.try_parse_domain_from_hex(search_domain)

    if domain is None:
        return handle_invalid_domain(search_domain)

    if fmt is None:
        return html_render(domain)
    elif fmt == 'json':
        return json_render(domain)
    elif fmt == 'csv':
        return csv_render(domain)
    else:
        flask.abort(400, 'Unknown export format: {}'.format(fmt))
