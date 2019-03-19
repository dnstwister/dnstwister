"""Launch."""
import threading
import waitress
import werkzeug.serving

import build.build_fed as build_fed
import dnstwister


@werkzeug.serving.run_with_reloader
def serve():
    """Run waitress, but reload with file system changes."""

    def builder_thread():
        build_fed.build('dnstwister/static/')
        build_fed.monitor('dnstwister/static/')
    threading.Thread(target=builder_thread).start()

    # Allow for template changes without manual restart.
    # At least until https://github.com/pallets/flask/pull/1910 is merged...
    dnstwister.app.jinja_env.auto_reload = True

    waitress.serve(
        dnstwister.app,
        host='0.0.0.0',
        port=5000,
    )
