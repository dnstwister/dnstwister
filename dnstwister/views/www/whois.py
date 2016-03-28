"""Index page."""
import flask

from dnstwister import app
import dnstwister.tools as tools


@app.route('/whois/<hexdomain>')
def whois_query(hexdomain):
    """Does a whois."""
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    whois_data = tools.whois_query(domain)

    return flask.render_template('www/whois.html', whois_data=whois_data)
