"""Root resources."""
import flask

from dnstwister import app
from dnstwister import cache


@cache.memoize(86400)
@app.route(r'/favicon.ico')
@app.route(r'/robots.txt')
@app.route(r'/sitemap.xml')
@app.route(r'/security.txt')
def favicon():
    """Favicon (because some clients don't read the link tag) as well as some
    other static files.
    """
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])
