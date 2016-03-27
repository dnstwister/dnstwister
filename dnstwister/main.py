"""dnstwister web app."""
import binascii
import datetime
import flask
import flask.ext.cache
import sys
import werkzeug.contrib.atom

import storage.pg_database


# Any implementation of storage.interfaces.IKeyValueDB.
db = storage.pg_database.PGDatabase()

# Import modules using main.db here.
import repository


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'No valid domains submitted.',
    'Invalid report URL.',
    'No domains submitted.',
)


app = flask.Flask(__name__)
cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})

# Import modules using main.cache here
import tools


@app.route('/ip/<hexdomain>')
def resolve(hexdomain):
    """Resolves Domains to IPs."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    ip, error = tools.resolve(domain)

    # Response IP is now an IP address, or False.
    return flask.json.jsonify({'ip': ip, 'error': error})


@app.route('/whois/<hexdomain>')
def whois_query(hexdomain):
    """Does a whois."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    whois_data = tools.whois_query(domain)

    return flask.render_template('whois.html', whois_data=whois_data)


@app.route('/atom/<hexdomain>')
def atom(hexdomain):
    """Return new atom items for changes in resolved domains."""
    # Parse out the requested domain
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    # Prepare a feed
    feed = werkzeug.contrib.atom.AtomFeed(
        title='dnstwister report for {}'.format(domain),
        feed_url='https://dnstwister.report/atom/{}'.format(hexdomain),
        url='https://dnstwister.report/search/{}'.format(hexdomain),
    )

    # The publish/update date for the placeholder is locked to 00:00:00.000
    # (midnight UTC) on the current day.
    today = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Ensure the domain is registered.
    if not repository.is_domain_registered(domain):
        repository.register_domain(domain)

    # Retrieve the delta report
    delta_report = repository.get_delta_report(domain)

    # If we don't have a delta report yet, show the placeholder.
    if delta_report is None:
        feed.add(
            title='No report yet for {}'.format(domain),
            title_type='text',
            content=flask.render_template(
                'atom_placeholder.html', domain=domain
            ),
            content_type='html',
            author='dnstwister',
            updated=today,
            published=today,
            id='waiting:{}'.format(domain),
            url=feed.url,
        )

    else:

        # If there is a delta report, generate the feed and return it. We use
        # the actual date of generation here.
        updated = repository.delta_report_updated(domain)
        if updated is None:
            updated = today

        # Setting the ID to be epoch seconds, floored per 24 hours, ensure the
        # updates are only every 24 hours max.
        id_24hr = (updated - datetime.datetime(1970, 1, 1)).total_seconds()

        common_kwargs = {
            'title_type': 'text',
            'content_type': 'text',
            'author': 'dnstwister',
            'updated': updated,
            'published': updated,
            'url': feed.url,
        }

        for (dom, ip) in delta_report['new']:
            feed.add(
                title='NEW: {}'.format(dom),
                content='IP: {}'.format(ip),
                id='new:{}:{}:{}'.format(dom, ip, id_24hr),
                **common_kwargs
            )

        for (dom, old_ip, new_ip) in delta_report['updated']:
            feed.add(
                title='UPDATED: {}'.format(dom),
                content='IP: {} > {}'.format(old_ip, new_ip),
                id='updated:{}:{}:{}:{}'.format(dom, old_ip, new_ip, id_24hr),
                **common_kwargs
            )

        for (dom, ip) in delta_report['deleted']:
            feed.add(
                title='DELETED: {}'.format(dom),
                content='IP: {}'.format(ip),
                id='deleted:{}:{}:{}'.format(dom, ip, id_24hr),
                **common_kwargs
            )

    feed_response = feed.get_response()

    repository.mark_delta_report_as_read(domain)

    return feed_response


@app.route('/report')
def report_old():
    """Redirect old bookmarked reports to the new path format."""
    try:
        path = flask.request.args['q']
    except:
        app.logger.error('Unable to decode valid domains from q GET param')
        return flask.redirect('/error/1')

    return flask.redirect('/search/{}'.format(path))


@app.route(r'/')
@app.route(r'/error/<error_arg>')
def index(error_arg=None):
    """Main page."""
    error = None
    try:
        error_idx = int(error_arg)
        assert error_idx >= 0
        error = ERRORS[error_idx]
    except:
        # This will fail on no error, an error that can't be converted to an
        # integer and an error that can be converted to an integer but is not
        # within the range of the tuple of errors. We don't need to log these
        # situations.
        pass

    return flask.render_template('index.html', error=error)


@app.route('/search', methods=['POST'])
@app.route('/search/<report_domains>')
@app.route('/search/<report_domains>/<format>')
def report(report_domains=None, format=None):
    """Handle reports."""

    def html_render(qry_domains):
        """Render and return the html report."""
        reports = dict(filter(None, map(tools.analyse, qry_domains)))

        # Handle no valid domains by redirecting to GET page.
        if len(reports) == 0:
            app.logger.error(
                'No valid domains found in {}'.format(qry_domains)
            )
            return flask.redirect('/error/0')

        return flask.render_template(
            'report.html',
            reports=reports,
            atoms=dict(zip(qry_domains, map(binascii.hexlify, qry_domains))),
            exports={'json':'json', 'csv': 'csv'},
            search=report_domains,
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

        return flask.Response(generate())#, mimetype='text/csv')

    if flask.request.method == 'GET':
        ### Handle redirect from form submit.
        # Try to parse out the list of domains
        try:
            qry_domains = map(
                tools.parse_domain,
                report_domains.split(',')
            )
        except:
            app.logger.error('Unable to decode valid domains from path')
            return flask.redirect('/error/1')

        if format is None:
            return html_render(qry_domains)
        elif format == 'json':
            return json_render(qry_domains)
        elif format == 'csv':
            return csv_render(qry_domains)
        else:
            flask.abort(500)

    else:
        # Handle form submit.
        qry_domains = tools.query_domains(flask.request.form)

        # Handle malformed domains data by redirecting to GET page.
        if qry_domains is None:
            app.logger.error(
                'No valid domains in POST dict {}'.format(flask.request.args)
            )
            return flask.redirect('/error/2')

        # Attempt to create a <= 200 character GET parameter from the domains
        # so we can redirect to that (allows bookmarking). As in '/ip' we use
        # hex to hide the domains from firewalls that already block some of
        # them.
        path = ','.join(map(binascii.hexlify, qry_domains))
        if len(path) <= 200:
            return flask.redirect('/search/{}'.format(path))

        # If there's a ton of domains, just to the report.
        return html_render(qry_domains)


@app.route('/email/subscribe/<b64domain>')
def email_subscribe_get_email(b64domain):
    """Handle subscriptions."""
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    return flask.render_template(
        'email/subscribe.html',
        domain=domain,
        b64domain=b64domain,
    )


@app.route('/email/subscribe/<b64domain>', methods=['POST'])
def email_subscribe_pending_confirm(b64domain):
    """Send email for verification of subscription."""
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    verify_code = tools.verify_code()
    print verify_code

    #TODO: err, send email? :)

    return flask.render_template('email/pending_verify.html', domain=domain)


@app.route('/email/verify/<verify_code>')
def email_subscribe_confirm_email(verify_code):
    """Handle email verification."""
    domain = 'www.example.com'
    return flask.render_template('email/subscribed.html', domain=domain)


if __name__ == '__main__':

    app.run(debug=(sys.argv[-1] == '-d'))
