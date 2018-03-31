"""Build the static files."""
import os
import sys
import time

import csscompressor
import watchdog.events
import watchdog.observers


maps = {
    'index.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'index.css',
    ),
    'analyse.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'analyse.css',
    ),
    'email.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'email.css',
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
    'analyse.min.js': (
        'jquery-1.11.3.min.js',
        'analyse.js',
    ),
    'status.min.css': (
        'normalize.css',
        'skeleton.css',
        'common.css',
        'status.css',
    ),
}


def build(root):
    print 'building...'
    for (dest, srcs) in maps.items():
        dest_data = []
        for src_file in srcs:
            src_path = os.path.join(root, 'sources/{}'.format(src_file))
            with open(src_path, 'rb') as srcf:
                dest_data.append(srcf.read())

        dest_data = '\n'.join(dest_data)

        if dest.endswith('.css'):
            dest_data = csscompressor.compress(dest_data)

        with open(os.path.join(root, dest), 'wb') as destf:
            destf.write(dest_data)


def monitor(root):

    class Handler(watchdog.events.FileSystemEventHandler):
        def on_any_event(*args):
            build(root)

    observer = watchdog.observers.Observer()
    observer.schedule(Handler(), os.path.join(root, 'sources/'))
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    build('../')
    if sys.argv[-1] == '--watch':
        monitor('../')
