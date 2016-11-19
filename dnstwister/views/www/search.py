"""Search/report page."""
import binascii
import json

import flask

from dnstwister import app
import dnstwister.tools as tools


def html_render(qry_domains, search_domains=None):
    """Render and return the html report."""
    reports = dict(filter(None, map(tools.analyse, qry_domains)))

    # Handle no valid domains by redirecting to GET page.
    if len(reports) == 0:
        app.logger.info(
            'No valid domains found in {}'.format(qry_domains)
        )
        return flask.redirect('/error/0')

    return flask.render_template(
        'www/report.html',
        reports=reports,
        atoms=dict(zip(qry_domains, map(binascii.hexlify, qry_domains))),
        exports={'json': 'json', 'csv': 'csv'},
        search=search_domains,
    )


def json_render(qry_domains):
    """Render and return the json-formatted report.

    The hand-assembly is due to the streaming of the response.
    """
    reports = dict(filter(None, map(tools.analyse, qry_domains)))

    def generate():
        """Streaming download generator."""

        yield '{\n'

        for (i, (dom, rept)) in enumerate(reports.items()):

            yield '"' + dom + '": {"fuzzy_domains": ['

            fuzzy_domains = rept['fuzzy_domains']
            for (j, entry) in enumerate(fuzzy_domains):

                ip_addr, error = tools.resolve(entry['domain-name'])
                data = {
                    'domain-name': entry['domain-name'],
                    'fuzzer': entry['fuzzer'],
                    'hex': entry['hex'],
                    'resolution': {
                        'error': error,
                        'ip': ip_addr,
                    },
                }

                yield json.dumps(data)
                if j < len(fuzzy_domains) - 1:
                    yield ','
                yield '\n'

            yield ']}'
            if i < len(reports) - 1:
                yield ','
            yield '\n'

        yield '}\n'

    return flask.Response(
        generate(),
        headers={
            'Content-Disposition': 'attachment; filename=dnstwister_report.json'
        },
        content_type='application/json'
    )


def csv_render(qry_domains):
    """Render and return the csv-formatted report."""
    headers = ('Domain', 'Type', 'Tweak', 'IP', 'Error')
    reports = dict(filter(None, map(tools.analyse, qry_domains)))

    def generate():
        """Streaming download generator."""
        yield ','.join(headers) + '\n'
        for (domain, rept) in reports.items():
            for entry in rept['fuzzy_domains']:
                ip_addr, error = tools.resolve(entry['domain-name'])
                row = map(str, (
                    domain,
                    entry['fuzzer'],
                    entry['domain-name'],
                    ip_addr,
                    error,
                ))
                yield ','.join(row) + '\n'

    return flask.Response(
        generate(),
        headers={
            'Content-Disposition': 'attachment; filename=dnstwister_report.csv'
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

    search_domains = tools.parse_post_data(post_data)

    valid_domains = sorted(list(set(filter(None, map(tools.parse_domain, search_domains)))))
    if len(valid_domains) == 0:
        app.logger.info(
            'No valid domains in POST {}'.format(flask.request.form)
        )
        suggestion = tools.suggest_domain(search_domains)
        if suggestion is not None:
            encoded_suggestion = binascii.hexlify(suggestion)
            return flask.redirect(
                '/error/0?suggestion={}'.format(encoded_suggestion)
            )
        return flask.redirect('/error/0')

    # Attempt to create a <= 200 character GET parameter from the domains so
    # we can redirect to that (allows bookmarking). As in '/api/analysis/ip'
    # we use hex to hide the domains from firewalls that already block some of
    # them.
    path = ','.join(map(binascii.hexlify, search_domains))
    if len(path) <= 200:
        return flask.redirect('/search/{}'.format(path))

    # If there's a ton of domains, just to the report.
    return html_render(search_domains)


@app.route('/search/<search_domains>')
@app.route('/search/<search_domains>/<fmt>')
def search(search_domains, fmt=None):
    """Handle redirect from form submit."""

    # Try to parse out the list of domains
    try:
        valid_domains = sorted(list(set(filter(None, map(
            tools.parse_domain, search_domains.split(',')
        )))))
    except:
        app.logger.info('Unable to decode valid domains from path')
        return flask.redirect('/error/0')

    if len(valid_domains) == 0:
        app.logger.info(
            'No valid domains in GET'
        )
        suggestion = tools.suggest_domain(search_domains.split(','))
        if suggestion is not None:
            encoded_suggestion = binascii.hexlify(suggestion)
            return flask.redirect(
                '/error/0?suggestion={}'.format(encoded_suggestion)
            )

        return flask.redirect('/error/0')

    if fmt is None:
        return html_render(valid_domains, search_domains)
    elif fmt == 'json':
        return json_render(valid_domains)
    elif fmt == 'csv':
        return csv_render(valid_domains)
    else:
        flask.abort(400, 'Unknown export format: {}'.format(fmt))


@app.route('/report')
def report_old():
    """Redirect old bookmarked reports to the new path format."""
    try:
        path = flask.request.args['q']
    except:
        app.logger.info('Unable to decode GET "q" param')
        return flask.redirect('/error/1')

    return flask.redirect('/search/{}'.format(path))
