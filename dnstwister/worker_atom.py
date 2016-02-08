"""Updates atom feeds."""
import time

import db
import tools


if __name__ == '__main__':
    while True:
        time.sleep(5)
        try:
            domain = db.stored_oldest()
            print 'Oldest: {}'.format(domain)

            existing = db.stored_get(domain)
            if existing is None:
                existing = {}

            latest = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                latest[entry['domain-name']] = ip

            db.stored_set(domain, latest)

            if latest == existing:
                print 'No change since last analysis'
                continue

        except Exception as ex:
            db.DB = None
            print 'crashed... {}'.format(ex)
