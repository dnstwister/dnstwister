"""Search/report page."""
import binascii
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
    """Render and return the json-formatted report."""
    reports = dict(filter(None, map(tools.analyse, qry_domains)))

    for rept in reports.values():
        for entry in rept['fuzzy_domains']:
            ip, error = tools.resolve(entry['domain-name'])
            entry['resolution'] = {
                'ip': ip,
                'error': error,
            }

    return flask.json.jsonify(reports)


def csv_render(qry_domains):
    """Render and return the csv-formatted report."""
    reports = dict(filter(None, map(tools.analyse, qry_domains)))

    def generate():
        """Streaming download generator."""
        for (domain, rept) in reports.items():
            for entry in rept['fuzzy_domains']:
                ip, error = tools.resolve(entry['domain-name'])
                row = map(str, (
                    domain,
                    entry['fuzzer'],
                    entry['domain-name'],
                    ip,
                    error,
                ))
                yield ','.join(row) + '\n'

    return flask.Response(generate(), mimetype='text/csv')


@app.route('/search', methods=['POST'])
def search_post():
    """Handle form submit."""
    qry_domains = tools.query_domains(flask.request.form)

    # Handle malformed domains data by redirecting to GET page.
    if qry_domains is None:
        app.logger.info(
            'No valid domains in POST dict {}'.format(flask.request.form)
        )
        return flask.redirect('/error/2')

    # Attempt to create a <= 200 character GET parameter from the domains so
    # we can redirect to that (allows bookmarking). As in '/api/analysis/ip'
    # we use hex to hide the domains from firewalls that already block some of
    # them.
    path = ','.join(map(binascii.hexlify, qry_domains))
    if len(path) <= 200:
        return flask.redirect('/search/{}'.format(path))

    # If there's a ton of domains, just to the report.
    return html_render(qry_domains)


@app.route('/search/<search_domains>')
@app.route('/search/<search_domains>/<format>')
def search(search_domains=None, format=None):
    """Handle redirect from form submit."""
    # Try to parse out the list of domains
    try:
        qry_domains = map(
            tools.parse_domain,
            search_domains.split(',')
        )
    except:
        app.logger.info('Unable to decode valid domains from path')
        return flask.redirect('/error/1')

    if format is None:
        return html_render(qry_domains, search_domains)
    elif format == 'json':
        return json_render(qry_domains)
    elif format == 'csv':
        return csv_render(qry_domains)
    else:
        flask.abort(400, 'Unknown export format')


@app.route('/report')
def report_old():
    """Redirect old bookmarked reports to the new path format."""
    try:
        path = flask.request.args['q']
    except:
        app.logger.info('Unable to decode valid domains from q GET param')
        return flask.redirect('/error/1')

    return flask.redirect('/search/{}'.format(path))
