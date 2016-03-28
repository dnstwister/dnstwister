"""Email pages."""
import flask

from dnstwister import app, repository
import dnstwister.tools as tools


@app.route('/email/subscribe/<hexdomain>')
def email_subscribe_get_email(hexdomain):
    """Handle subscriptions."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    return flask.render_template(
        'www/email/subscribe.html',
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

    return flask.render_template('www/email/pending_verify.html', domain=domain)


@app.route('/email/verify/<hexdomain>/<verify_code>')
def email_subscribe_confirm_email(hexdomain, verify_code):
    """Handle email verification."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    if not repository.verify_code_valid(verify_code):
        flask.abort(500)

    repository.subscribe_email(verify_code, domain)

    return flask.render_template('www/email/subscribed.html', domain=domain)
