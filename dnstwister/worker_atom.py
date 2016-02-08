"""Updates atom feeds."""
import collections
import time

import db
import tools


if __name__ == '__main__':
    while True:
        time.sleep(5)
        try:
            start = time.time()

            # Pick the oldest domain.
            domain = db.stored_oldest()

            # Recover the last report.
            existing = db.stored_get(domain)
            if existing is None:
                existing = {}

            # Generate a new report.
            latest = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                latest[entry['domain-name']] = ip

            # Saving ensures the last-updated it ticked over.
            db.stored_set(domain, latest)

            if latest != existing:

                # Generate the CRUD report.
                report = collections.defaultdict(list)
                for (dom, ip) in latest.items():
                    if dom in existing:
                        if ip == existing[dom]:
                            continue
                        else:
                            report['updated'].append((dom, ip))
                    else:
                        report['new'].append((dom, ip))

                db.report_set(domain, dict(report))

            print ','.join(map(str, (
                domain, latest == existing, time.time() - start
            )))

        except Exception as ex:
            db.DB = None
            print 'crashed... {}'.format(ex)
