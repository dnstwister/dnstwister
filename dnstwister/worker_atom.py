"""Updates atom feeds."""
import datetime
import time

import deltas
import reports
import tools


# Time in seconds between re-processing a domain.
PERIOD = 86400


if __name__ == '__main__':
    while True:


        try:
            start = time.time()

            # Pick the oldest delta.
            domain = deltas.oldest()

            if domain is None:
                print 'No deltas...'
                time.sleep(10)
                continue

            # Get the existing report
            old_report = reports.get(domain)

            if old_report is None:
                old_report = {}

            # Create a new report
            new_report = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                new_report[entry['domain-name']] = ip

            # Store it
            reports.update(domain, new_report)

            # Create a delta report
            delta = {'new': [], 'updated': [], 'deleted': []}

            for (ip, dom) in new_report.items():
                if dom in old_report.keys():
                    if ip != old_report[dom]:
                        delta['updated'].append((dom, old_report[dom], ip))
                else:
                    delta['new'].append((dom, ip))

            for (ip, dom) in old_report.items():
                if dom not in new_report.keys():
                    delta['deleted'].append(dom)

            # Store it
            deltas.update(domain, delta)

        except Exception as ex:
            print 'crashed... {}'.format(ex)
            time.sleep(10)
