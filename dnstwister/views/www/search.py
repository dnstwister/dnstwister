"""Search/report page."""
import binascii
import json

import flask

from dnstwister import app
import dnstwister.tools as tools


def html_render(qry_domains, search_domains=None):
    """Render and return the html report."""
    reports = dict([_f for _f in map(tools.analyse, qry_domains) if _f])

    # Handle no valid domains by redirecting to GET page.
    if len(reports) == 0:
        app.logger.info(
            'No valid domains found in {}'.format(qry_domains)
        )
        return flask.redirect('/error/0')

    return flask.render_template(
        'www/report.html',
        reports=reports,
        atoms=dict(list(zip(qry_domains, list(map(binascii.hexlify, qry_domains))))),
        exports={'json': 'json', 'csv': 'csv'},
        search=search_domains,
    )


def json_render(qry_domains):
    """Render and return the json-formatted report.

    The hand-assembly is due to the streaming of the response.
    """
    reports = dict([_f for _f in map(tools.analyse, qry_domains) if _f])

    def generate():
        """Streaming download generator."""
        indent_size = 4
        indent = ' ' * indent_size

        yield '{\n'

        for (i, (dom, rept)) in enumerate(reports.items()):

            yield indent + '"' + dom + '": {\n'
            yield indent * 2 + '"fuzzy_domains": [\n'

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

                json_str = json.dumps(
                    data,
                    sort_keys=True,
                    indent=indent_size,
                    separators=(',', ': ')
                )
                yield '\n'.join([indent * 3 + line
                                 for line
                                 in json_str.split('\n')])
                if j < len(fuzzy_domains) - 1:
                    yield ','
                yield '\n'

            yield indent * 2 + ']\n'
            yield indent + '}'
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
    reports = dict([_f for _f in map(tools.analyse, qry_domains) if _f])

    def generate():
        """Streaming download generator."""
        yield ','.join(headers) + '\n'
        for (domain, rept) in list(reports.items()):
            for entry in rept['fuzzy_domains']:
                ip_addr, error = tools.resolve(entry['domain-name'])
                row = list(map(str, (
                    domain,
                    entry['fuzzer'],
                    entry['domain-name'],
                    ip_addr,
                    error,
                )))
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

    valid_domains = sorted(list(set([_f for _f in map(tools.parse_domain, search_domains) if _f])))
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
    path = ','.join([str(binascii.hexlify(domain.encode('utf8')), 'ascii')
                     for domain
                     in search_domains])
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
        valid_domains = sorted(list(set([_f for _f in map(
            tools.parse_domain, search_domains.split(',')
        ) if _f])))
    except:
        app.logger.info('Unable to decode valid domains from path')
        return flask.redirect('/error/0')

    if len(valid_domains) == 0:
        app.logger.info(
            'No valid domains in GET'
        )
        suggestion = tools.suggest_domain(search_domains.split(','))
        if suggestion is not None:
            encoded_suggestion = str(
                binascii.hexlify(suggestion.encode('utf8')),
                'ascii'
            )
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
