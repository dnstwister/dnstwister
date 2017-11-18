"""Index page."""
import flask

from dnstwister import app
import dnstwister.tools as tools


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'Invalid domain submitted.',
    'Invalid report URL.',
    'No domain submitted.',
)


@app.route(r'/')
@app.route(r'/error/<error_arg>')
def index(error_arg=None):
    """Main page."""
    error = None
    error_idx = None
    suggestion = None

    try:
        if error_arg is not None:
            error_idx = int(error_arg)
            if error_idx >= 0:
                error = ERRORS[error_idx]
    except (TypeError, ValueError, IndexError):
        # This will fail an error index that can't be converted to an
        # integer and an error index that can be converted to an integer
        # but is not within the range of the tuple of errors.
        app.logger.info(
            'Invalid value passed for error index: {}'.format(error_idx)
        )

    if error_idx == 0:
        encoded_suggestion = flask.request.args.get('suggestion')
        suggestion = tools.parse_domain(encoded_suggestion)

    return flask.render_template(
        'www/index.html', error=error, suggestion=suggestion
    )
