"""The analysis API endpoint."""
import flask
import urlparse


app = flask.Blueprint('api_entry', __name__)


@app.route('/')
def api_definition():
    return flask.jsonify({
        'url': flask.request.base_url,
        'domain_analysis_url': urlparse.urljoin(
            flask.request.url_root, flask.url_for('analysis_api.api_definition')
        ),
    })
