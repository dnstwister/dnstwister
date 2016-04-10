"""Email pages."""
import flask

from dnstwister import app, emailer, gateway, repository
import dnstwister.tools as tools
import dnstwister.tools.email as email_tools


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


@app.route('/email/pending_verify/<hexdomain>', methods=['POST'])
def email_subscribe_pending_confirm(hexdomain):
    """Send a confirmation email for a user."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    email_address = flask.request.form['email_address']
    verify_code = tools.random_id()
    verify_url = flask.request.url_root + 'email/verify/{}'.format(verify_code)
    email_body = email_tools.render_email(
        'confirm.html',
        domain=domain,
        verify_url=verify_url
    )

    repository.propose_subscription(verify_code, email_address, domain)
    emailer.send(
        email_address, 'Please verify your subscription', email_body
    )

    return flask.render_template('www/email/pending_verify.html', domain=domain)


@app.route('/email/verify/<verify_code>')
def email_subscribe_confirm_email(verify_code):
    """Handle email verification."""
    pending_verify = repository.get_proposition(verify_code)

    if pending_verify is None:
        flask.abort(500)

    email_address = pending_verify['email_address']
    domain = pending_verify['domain']
    sub_id = tools.random_id()

    repository.subscribe_email(sub_id, email_address, domain)
    repository.remove_proposition(verify_code)

    return flask.render_template('www/email/subscribed.html', domain=domain)


@app.route('/email/unsubscribe/<sub_id>')
def unsubscribe_user(sub_id):
    """Unsubscribe a user from a domain."""
    repository.unsubscribe(sub_id)
    return flask.render_template('www/email/unsubscribed.html')
