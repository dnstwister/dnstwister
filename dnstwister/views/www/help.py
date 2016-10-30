"""Help page.

Currently a redirect to RTD.
"""
import flask

from dnstwister import app


RTD_STABLE = 'https://dnstwister.readthedocs.org/en/stable/web.html'


@app.route(r'/help')
def help_redirect():
    """Help redirect."""
    return flask.redirect(RTD_STABLE)
