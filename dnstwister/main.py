""" DNS Twister web app.
"""
import base64
import flask
import flask.ext.cache
import socket
import datetime
import urllib
import werkzeug.contrib.atom

import tools


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


@app.route('/atom/<b64domain>')
@cache.cached(timeout=86400)
def atom(b64domain):
    """Atom feed functionality.

    Cached to 24 hours to reduce load. Only returns resolved IPs.
    """
    domain = tools.parse_domain(b64domain)
    if domain is None:
        flask.abort(500)

    feed = werkzeug.contrib.atom.AtomFeed(
        title='DNS Twister matches for {}'.format(domain),
        feed_url='https://dnstwister.report/atom/{}'.format(b64domain),
        url='https://dnstwister.report/report/?q={}'.format(b64domain),
    )

    for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:

        ip, error = tools.resolve(entry['domain-name'])

        if ip is None or error == True:
            continue

        feed.add(
            title=entry['domain-name'],
            title_type='text',
            content='{} ({})'.format(ip, entry['fuzzer']),
            content_type='text',
            author='DNS Twister',
            updated=datetime.datetime.now(),
            id='{}:{}'.format(domain, entry['domain-name']),
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

        return flask.render_template('report.html', reports=reports)

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

    app.run(debug=False)
