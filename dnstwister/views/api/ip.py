"""API page."""
import flask

from dnstwister import app


@app.route('/ip/<hexdomain>')
def resolve(hexdomain):
    """Resolves Domains to IPs."""
    return flask.redirect(
        flask.url_for('analysis_api.ip', hexdomain=hexdomain), 301
    )
