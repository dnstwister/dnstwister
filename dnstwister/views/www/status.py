"""Status page.

This page requires an external data source returning JSON data to function
correctly, something that is not part of the GitHub repository.
"""
import os

import flask
import requests

from dnstwister import app


@app.route(r'/status')
def status():
    """Status page."""
    try:
        status_data = requests.get(os.environ['MONITORING_DATACLIP']).json()
    except Exception as ex:
        app.logger.error(
            'Unable to retrieve monitoring dataclip: {}'.format(ex)
        )
        flask.abort(500)

    return flask.render_template(
        'www/status.html',
        summary=all(status_data['values'][0]),
        statuses=zip(status_data['fields'], status_data['values'][0])
    )
