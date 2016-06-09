"""The analysis API endpoint."""
import flask
import urlparse


app = flask.Blueprint('api_entry', __name__)


@app.route('/')
def api_definition():
    """API definition."""
    return flask.jsonify({
        'url': flask.request.base_url,
        'dnstwist_api_url': urlparse.urljoin(
            flask.request.url_root, flask.url_for('dnstwist_api.api_definition')
        ),
        'domain_analysis_api_url': urlparse.urljoin(
            flask.request.url_root, flask.url_for('analysis_api.api_definition')
        ),
    })
