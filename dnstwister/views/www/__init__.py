"""Root resources."""
import flask

from dnstwister import app
from dnstwister import cache


@cache.memoize(86400)
@app.route(r'/favicon.ico')
def favicon():
    """Favicon (because some clients don't read the link tag)."""
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])
