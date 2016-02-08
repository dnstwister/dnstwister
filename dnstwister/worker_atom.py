"""Updates atom feeds."""
import collections
import time

import db
import tools


if __name__ == '__main__':
    while True:
        time.sleep(1)
        try:
            start = time.time()

            # Pick the oldest domain.
            domain = db.stored_oldest()

            # Generate a new report.
            latest = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                latest[entry['domain-name']] = ip

            # Update the "latest" version of the report.
            db.stored_set(domain, latest)

            print ','.join(map(str, (
                domain, time.time() - start
            )))

        except Exception as ex:
            db.DB = None
            print 'crashed... {}'.format(ex)
