"""Search/report page."""
import json

import flask

from dnstwister import app
import dnstwister.tools as tools


def html_render(domain):
    """Render and return the html report."""
    reports = dict([tools.analyse(domain)])

    return flask.render_template(
        'www/report.html',
        reports=reports,
        atoms=dict([(domain, tools.encode_domain(domain))]),
        exports={'json': 'json', 'csv': 'csv'},
        search=[domain],
    )


def json_render(domain):
    """Render and return the json-formatted report.

    The hand-assembly is due to the streaming of the response.
    """
    reports = dict([tools.analyse(domain)])

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


def csv_render(domain):
    """Render and return the csv-formatted report."""
    headers = ('Domain', 'Type', 'Tweak', 'IP', 'Error')
    reports = dict([tools.analyse(domain)])

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

    search_parameter = tools.encode_domain(post_data)

    return flask.redirect('/search/{}'.format(search_parameter))


def handle_invalid_domain(search_term_as_hex):
    """Called when no valid domain found in GET param, creates a suggestion
    to return to the user.
    """
    decoded_search = None
    try:
        decoded_search = tools.decode_domain(search_term_as_hex)
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
            encoded_suggestion = tools.encode_domain(suggestion)
            return flask.redirect(
                '/error/0?suggestion={}'.format(encoded_suggestion)
            )

    app.logger.info(
        'Not a valid domain in GET: {}'.format(search_term_as_hex)
    )
    return flask.redirect('/error/0')


@app.route('/search/<search_domain>')
@app.route('/search/<search_domain>/<fmt>')
def search(search_domain, fmt=None):
    """Handle redirect from form submit."""
    domain = tools.parse_post_data(search_domain)

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


@app.route('/report')
def report_old():
    """Redirect old bookmarked reports to the new path format."""
    try:
        path = flask.request.args['q']
    except:
        app.logger.info('Unable to decode GET "q" param')
        return flask.redirect('/error/1')

    return flask.redirect('/search/{}'.format(path))
