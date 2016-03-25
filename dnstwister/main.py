"""dnstwister web app."""
import base64
import datetime
import flask
import flask.ext.cache
import sys
import urllib
import werkzeug.contrib.atom

import storage.pg_database
import tools


# Any implementation of storage.interfaces.IKeyValueDB.
db = storage.pg_database.PGDatabase()

# Set up the repository. Will import main.db.
import repository


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'No valid domains submitted.',
    'Invalid report URL.',
    'No domains submitted.',
)


app = flask.Flask(__name__)

cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/ip/<b64domain>')
@cache.cached(timeout=86400)
def resolve(b64domain):
    """Resolves Domains to IPs.

    Cached to 24 hours.
    """
    # Firstly, try and parse a valid domain (base64-encoded) from the
    # 'b64' GET parameter.
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    ip, error = tools.resolve(domain)

    # Response IP is now an IP address, or False.
    return flask.json.jsonify({'ip': ip, 'error': error})


@app.route('/whois/<b64domain>')
@cache.cached(timeout=86400)
def whois_query(b64domain):
    """Does a whois.

    Cached to 24 hours.
    """
    # Firstly, try and parse a valid domain (base64-encoded) from the
    # 'b64' GET parameter.
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    whois_data = tools.whois_query(domain)

    return flask.render_template('whois.html', whois_data=whois_data)


@app.route('/atom/<b64domain>')
@cache.cached(timeout=86400)
def atom(b64domain):
    """Return new atom items for changes in resolved domains.

    Cached for 24 hours.
    """
    # Parse out the requested domain
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    # Prepare a feed
    feed = werkzeug.contrib.atom.AtomFeed(
        title='dnstwister report for {}'.format(domain),
        feed_url='https://dnstwister.report/atom/{}'.format(b64domain),
        url='https://dnstwister.report/report?q={}'.format(b64domain),
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
        return feed.get_response()

    # If there is a delta report, generate the feed and return it. We use the
    # actual date of generation here.
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

    return feed.get_response()


@app.route('/report', methods=['GET', 'POST'])
def report():
    """Handle reports."""
    def render_report(qry_domains):
        """ Render and return the report.
        """
        reports = dict(filter(None, map(tools.analyse, qry_domains)))

        # Handle no valid domains by redirecting to GET page.
        if len(reports) == 0:
            app.logger.error(
                'No valid domains found in {}'.format(qry_domains)
            )
            return flask.redirect('/error/0')

        return flask.render_template(
            'report.html', reports=reports,
            atoms=dict(zip(qry_domains, map(base64.b64encode, qry_domains)))
        )

    if flask.request.method == 'GET':
        ### Handle redirect from form submit.
        # Try to parse out the list of domains
        try:
            qry_domains = map(
                base64.b64decode,
                flask.request.args['q'].split(',')
            )
        except:
            app.logger.error('Unable to decode valid domains from q GET param')
            return flask.redirect('/error/1')

        return render_report(qry_domains)

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
        # b64 to hide the domains from firewalls that already block some of
        # them.
        params = urllib.urlencode({
            'q': ','.join(map(base64.b64encode, qry_domains))
        })
        if len(params) <= 200:
            return flask.redirect('/report?{}'.format(params))

        # If there's a ton of domains, just to the report.
        return render_report(qry_domains)


@app.route(r'/')
@app.route(r'/error/<error_arg>')
@cache.cached(timeout=3600)
def index(error_arg=None):
    """Main page, cached to 2 hours."""
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


if __name__ == '__main__':

    app.run(debug=(sys.argv[-1] == '-d'))
