"""Build the static files. Cloudflare minifies so this just concatenates."""
import sys


maps = {
    'index.min.css': (
        'normalize.css',
        'skeleton.css',
        'index.css',
    ),
    'whois.min.css': (
        'normalize.css',
        'skeleton.css',
    ),
    'report.min.css': (
        'normalize.css',
        'skeleton.css',
        'report.css',
    ),
    'report.min.js': (
        'jquery-1.11.3.min.js',
        'report.js',
    ),
}


def build():
    print 'building...'
    for (dest, srcs) in maps.items():
        dest_data = []
        for src in srcs:
            with open('sources/{}'.format(src), 'rb') as srcf:
                dest_data.append(srcf.read())

        with open(dest, 'wb') as destf:
            destf.write('\n'.join(dest_data))



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
