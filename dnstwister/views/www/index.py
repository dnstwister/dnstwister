"""Index page."""
import flask

from dnstwister import app
import dnstwister.tools as tools


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'No valid domains submitted.',
    'Invalid report URL.',
    'No domains submitted.',
)


@app.route(r'/')
@app.route(r'/error/<error_arg>')
def index(error_arg=None):
    """Main page."""
    error = None
    error_idx = None
    suggestion = None

    try:
        error_idx = int(error_arg)
        if error_idx >= 0:
            error = ERRORS[error_idx]
    except:
        # This will fail on no error, an error that can't be converted to an
        # integer and an error that can be converted to an integer but is not
        # within the range of the tuple of errors. We don't need to log these
        # situations.
        pass

    if error_idx == 0:
        try:
            encoded_suggestion = flask.request.args['suggestion']
            suggestion = tools.parse_domain(encoded_suggestion)
        except:
            pass

    return flask.render_template(
        'www/index.html', error=error, suggestion=suggestion
    )
