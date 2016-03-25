"""Updates atom feeds."""
import datetime
import time

import dnstwist
import repository
import tools


# Time in seconds between re-processing a domain.
PERIOD = 86400

# Multiplier on period to unregister if not read.
UNREGISTER = 7


if __name__ == '__main__':
    while True:

        domains_iter = repository.iregistered_domains()

        while True:
            try:
                domain = domains_iter.next()
            except StopIteration:
                break

            if dnstwist.validate_domain(domain) is None:
                print 'Unregistering (invalid) {}'.format(domain)
                repository.unregister_domain(domain)
                continue

            # Unregister long-time unread domains
            last_read = repository.delta_report_last_read(domain)
            if last_read is None:
                repository.mark_delta_report_as_read(domain)
            else:
                age = datetime.datetime.now() - last_read
                if age > datetime.timedelta(seconds=PERIOD*UNREGISTER):
                    print 'Unregistering {}'.format(domain)
                    repository.unregister_domain(domain)
                    continue

            # Skip domains that have been recently updated
            delta_last_updated = repository.delta_report_updated(domain)
            if delta_last_updated is not None:
                age = datetime.datetime.now() - delta_last_updated
                if age < datetime.timedelta(seconds=PERIOD):
                    print 'Skipping {}'.format(domain)
                    continue

            start = time.time()

            existing_report = repository.get_resolution_report(domain)

            if existing_report is None:
                existing_report = {}

            new_report = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                new_report[entry['domain-name']] = ip

            repository.update_resolution_report(domain, new_report)

            delta_report = {'new': [], 'updated': [], 'deleted': []}
            for (dom, ip) in new_report.items():
                if dom in existing_report.keys():
                    if ip != existing_report[dom]:
                        delta_report['updated'].append(
                            (dom, existing_report[dom], ip)
                        )
                else:
                    delta_report['new'].append((dom, ip))
            for (dom, ip) in existing_report.items():
                if dom not in new_report.keys():
                    delta_report['deleted'].append(dom)

            repository.update_delta_report(domain, delta_report)

            print 'Updated deltas for {} in {} seconds'.format(
                domain, time.time() - start
            )

        time.sleep(60)
