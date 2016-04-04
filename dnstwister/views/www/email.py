"""Email pages."""
import flask

from dnstwister import app, emailer, gateway, repository
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
        public_key=gateway.widget_public_key,
    )


@app.route('/email/subscribe/<hexdomain>', methods=['POST'])
def email_subscribe_pending_confirm(hexdomain):
    """Attach user to paid subscription for a domain."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    token = flask.request.form['stripeToken']
    email = flask.request.form['stripeEmail']

    payment_customer_id = gateway.charge(token, email)

    sub_id = tools.subscription_id()

    repository.subscribe_email(sub_id, email, domain, payment_customer_id)

    return flask.render_template('www/email/subscribed.html', domain=domain)


@app.route('/email/unsubscribe/<sub_id>', methods=['POST'])
def unsubscribe_user(sub_id):
    """Unsubscribe a user from a domain."""
    sub = repository.subscription(sub_id)

    if sub is None:
        flask.abort(500)

    customer_id = sub['payment_customer_id']

    gateway.cancel(customer_id)

    repository.unsubscribe(sub_id)

    domain = sub['domain']

    return flask.render_template('www/email/unsubscribed.html', domain=domain)
