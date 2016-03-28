"""Index page."""
import flask

from dnstwister import app


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
    try:
        error_idx = int(error_arg)
        assert error_idx >= 0
        error = ERRORS[error_idx]
    except:
        # This will fail on no error, an error that can't be converted to an
        # integer and an error that can be converted to an integer but is not
        # within the range of the tuple of errors. We don't need to log these
        # situations.
        pass

    return flask.render_template('www/index.html', error=error)
