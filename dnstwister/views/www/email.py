"""Email pages."""
import operator

import flask

from dnstwister import app, emailer, repository, stats_store
import dnstwister.tools as tools
import dnstwister.tools.email as email_tools


ERRORS = (
    'Email address is required',
)


@app.route('/email/subscribe/<hexdomain>')
@app.route('/email/subscribe/<hexdomain>/<error>')
def email_subscribe_get_email(hexdomain, error=None):
    """Handle subscriptions."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(400, 'Malformed domain or domain not represented in hexadecimal format.')

    # Attempt to parse out a validation error.
    error_str = None
    try:
        if error is not None:
            error_idx = int(error)
            if error_idx >= 0:
                error_str = ERRORS[error_idx]
    except:
        app.logger.info(
            'Invalid error index {}'.format(error)
        )

    return flask.render_template(
        'www/email/subscribe.html',
        domain=domain,
        hexdomain=hexdomain,
        error=error_str,
    )


@app.route('/email/pending_verify/<hexdomain>', methods=['POST'])
def email_subscribe_pending_confirm(hexdomain):
    """Send a confirmation email for a user."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(400, 'Malformed domain or domain not represented in hexadecimal format.')

    email_address = flask.request.form['email_address']

    if email_address.strip() == '':
        return flask.redirect('/email/subscribe/{}/0'.format(hexdomain))

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
        app.logger.info(
            'Failed to verify a non-existent subscription with id: {}'.format(verify_code)
        )
        return flask.redirect('/')

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


@app.route('/email/<sub_id>/noisy')
def email_view_noisy_domains(sub_id):
    """Show the noisy domains not sent in the email.

    This is deliberately bound to the email system as the detection of noisy
    domains is limited to the domains found in email subscriptions.
    """
    subscribed_domain = repository.subscribed_domain(sub_id)
    if subscribed_domain is None:
        app.logger.info(
            'Failed to retrieve sub for id for noisy report: {}'.format(sub_id)
        )
        return flask.redirect('/')

    fuzzy_domains = map(
        operator.itemgetter('domain-name'),
        tools.fuzzy_domains(subscribed_domain)
    )

    noisy_domains = [domain
                     for domain
                     in fuzzy_domains
                     if stats_store.is_noisy(domain)]

    return flask.render_template(
        'www/email/noisy.html',
        domain=subscribed_domain,
        noisy_domains=noisy_domains
    )
