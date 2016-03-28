"""dnstwister web app."""
import flask
import flask.ext.cache

import storage.pg_database

# Set up app/cache/db here
app = flask.Flask(__name__)
db = storage.pg_database.PGDatabase()
cache = flask.ext.cache.Cache(app, config={'CACHE_TYPE': 'simple'})

# Import modules using dnstwister.app/cache/db here
import repository
import tools
import views.syndication.atom
import views.www.index
import views.www.search
import views.www.whois


@app.route('/ip/<hexdomain>')
def resolve(hexdomain):
    """Resolves Domains to IPs."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    ip, error = tools.resolve(domain)

    # Response IP is now an IP address, or False.
    return flask.json.jsonify({'ip': ip, 'error': error})


@app.route('/email/subscribe/<hexdomain>')
def email_subscribe_get_email(hexdomain):
    """Handle subscriptions."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    return flask.render_template(
        'email/subscribe.html',
        domain=domain,
        hexdomain=hexdomain,
    )


@app.route('/email/subscribe/<hexdomain>', methods=['POST'])
def email_subscribe_pending_confirm(hexdomain):
    """Send email for verification of subscription."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    email = flask.request.form['email']

    verify_code = tools.verify_code()
    print verify_code

    repository.stage_email_subscription(email, verify_code)

    #TODO: err, send email? :)

    return flask.render_template('email/pending_verify.html', domain=domain)


@app.route('/email/verify/<hexdomain>/<verify_code>')
def email_subscribe_confirm_email(hexdomain, verify_code):
    """Handle email verification."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    if not repository.verify_code_valid(verify_code):
        flask.abort(500)

    repository.subscribe_email(verify_code, domain)

    return flask.render_template('email/subscribed.html', domain=domain)
