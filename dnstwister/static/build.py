"""Build the static files.

Requires: pip install csscompressor

Cloudflare compresses JS for us.
"""
import csscompressor
import sys


maps = {
    'index.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'index.css',
    ),
    'whois.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
    ),
    'email.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
    ),
    'report.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'report.css',
    ),
    'report.min.js': (
        'jquery-1.11.3.min.js',
        'report.js',
    ),
    'status.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'status.css',
    ),
}


def build():
    print 'building...'
    for (dest, srcs) in maps.items():
        dest_data = []
        for src in srcs:
            with open('sources/{}'.format(src), 'rb') as srcf:
                dest_data.append(srcf.read())

        dest_data = '\n'.join(dest_data)

        if dest.endswith('.css'):
            dest_data = csscompressor.compress(dest_data)

        with open(dest, 'wb') as destf:
            destf.write(dest_data)


if __name__ == '__main__':

    build()
    if sys.argv[-1] == '--watch':
        import time
        import watchdog.events
        import watchdog.observers

        class Handler(watchdog.events.FileSystemEventHandler):
            def on_any_event(*args):
                build()

        observer = watchdog.observers.Observer()
        observer.schedule(Handler(), './sources')
        observer.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
