"""Index page."""
import flask
import os
import requests

from dnstwister import app
from dnstwister import cache


@app.route(r'/status')
@cache.memoize(300) # 5 minutes
def status():
    """Status page."""
    try:
        status_data = requests.get(os.environ['MONITORING_DATACLIP']).json()
    except Exception as ex:
        app.logger.error(
            'Unable to retrieve monitoring dataclip: {}'.format(ex)
        )
        flask.abort(500)

    return flask.render_template('www/status.html',
        summary= all(status_data['values'][0]),
        statuses=zip(status_data['fields'], status_data['values'][0])
    )
