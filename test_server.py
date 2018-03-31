"""Launch."""
import os

import waitress
import werkzeug.serving

import dnstwister


@werkzeug.serving.run_with_reloader
def serve():
    """Run waitress, but reload with file system changes."""

    # Allow for template changes without manual restart.
    # At least until https://github.com/pallets/flask/pull/1910 is merged...
    dnstwister.app.jinja_env.auto_reload = True

    waitress.serve(
        dnstwister.app,
        host='0.0.0.0',
        port=5000,
    )


if __name__ == '__main__':
    serve()
