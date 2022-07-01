"""Launch."""
import sys
import threading

import hupper
import waitress

import build.build_fed as build_fed


def serve(args=sys.argv[1:]):
    """Run waitress, but reload with file system changes."""
    if '--reload' in args:
        reloader = hupper.start_reloader('local_server.serve')

    def builder_thread():
        build_fed.build('dnstwister/static/')
        build_fed.monitor('dnstwister/static/')
    threading.Thread(target=builder_thread).start()

    import dnstwister

    # Allow for template changes without manual restart.
    # At least until https://github.com/pallets/flask/pull/1910 is merged...
    dnstwister.app.jinja_env.auto_reload = True

    waitress.serve(
        dnstwister.app,
        host='127.0.0.1',
        port=5000,
    )


if __name__ == '__main__':
    serve()
