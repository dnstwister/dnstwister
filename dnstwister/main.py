""" DNS Twister web app.
"""
import base64
import flask
import flask_sslify
import os
import socket
import urllib
import werkzeug.contrib.fixers

import tools


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'No valid domains submitted.',
    'Invalid report URL.',
    'No domains submitted.',
)


app = flask.Flask(__name__)


@app.route('/ip')
def resolve_ip():
    """ Resolves Domains to IPs.

        We double-handle off another appspot app as gethostbyname() isn't
        implemented in GAE for Python?!?!?!
    """
    # We assume we don't resolve the IP but that we had no error in the
    # attempt.
    ip = None
    error = False

    # Firstly, try and parse a valid domain (base64-encoded) from the
    # 'b64' GET parameter.
    domain = tools.parse_domain(flask.request.args)
    if domain is None:
        app.logger.error('Unable to decode valid domain from b64 GET param')
        flask.abort(500)

    # Next, attempt to resolve via memcache. This returns None if not
    # found, as opposed to False when we found it but it didn't resolve
    # last time.
    try:

        ip = socket.gethostbyname(domain)

    except socket.gaierror:

        # Indicates failure to resolve to IP address, not an error in
        # the attempt.
        ip = False

    # Response IP is now an IP address, or False.
    return flask.json.jsonify({'ip': ip, 'error': error})


@app.route('/report', methods=['GET', 'POST'])
def report():
    """ Handle reports.
    """
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
def index(error_arg=None):
    """ Main page, if there is an error to render.
    """
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

    # Force SSL under Heroku
    if 'DYNO' in os.environ:
        app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)
        sslify = flask_sslify.SSLify(app)

    app.run(debug=True)
