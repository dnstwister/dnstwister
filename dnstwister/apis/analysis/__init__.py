"""The analysis API endpoint."""
import flask
import urlparse

import checks.parked as parked
import dnstwister.tools as tools

app = flask.Blueprint('api', __name__, template_folder='templates')


def api_url(view, var_pretty_name):
    """Create nice API urls."""
    view_path = '.{}'.format(view.func_name)
    route_var = view.func_code.co_varnames[:view.func_code.co_argcount][0]
    path = flask.url_for(view_path, **{route_var: ''})
    path += '{' + var_pretty_name + '}'
    return urlparse.urljoin(
        flask.request.url_root,
        path
    )


@app.route('/')
def api_definition():
    return flask.jsonify({
        'parked_check_url': api_url(parked_score, 'domain_as_hex'),
    })


@app.route('/parked/<hexdomain>')
def parked_score(hexdomain):
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)
    return flask.jsonify({'score': parked.get_score(domain)})
