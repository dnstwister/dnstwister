"""Root resources."""
import flask

from dnstwister import app


@app.route(r'/favicon.ico')
def favicon():
    """Favicon (because some clients don't read the link tag)."""
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])


@app.errorhandler(404)
def page_not_found(e):
    if flask.request.path.startswith('/api/'):
        return flask.jsonify(error='Resource not found.'), 404
    return flask.render_template('www/error/404.html'), 404


@app.errorhandler(400)
def bad_request(e):
    if flask.request.path.startswith('/api/'):
        return flask.jsonify(error=str(e.description)), 400
    return flask.render_template('www/error/400.html', error=e.description), 400
