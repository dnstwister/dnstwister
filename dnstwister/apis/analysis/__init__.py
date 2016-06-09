"""The analysis API endpoint."""
import flask

import checks.parked as parked
import dnstwister.tools as tools

app = flask.Blueprint('api', __name__, template_folder='templates')


@app.route('/parked/<hexdomain>')
def parked_score(hexdomain):
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    return flask.jsonify({'score': parked.get_score(domain)})
