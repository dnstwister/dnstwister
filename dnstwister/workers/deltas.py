"""Updates atom feeds."""
import datetime
import time

from dnstwister import repository
import dnstwister.tools as tools
import dnstwister.dnstwist as dnstwist

# Time in seconds between re-processing a domain.
PERIOD = 86400  # 24 hours

# Multiplier on period to unregister if not read.
UNREGISTER = 3  # 3 days


def process_domain(domain):
    """Process a domain - generating resolution reports and deltas."""
    if dnstwist.validate_domain(domain) is None:
        print 'Unregistering (invalid) {}'.format(domain.encode('idna'))
        repository.unregister_domain(domain)
        return

    # Unregister long-time unread domains
    last_read = repository.delta_report_last_read(domain)
    if last_read is None:
        repository.mark_delta_report_as_read(domain)
    else:
        age = datetime.datetime.now() - last_read
        if age > datetime.timedelta(seconds=PERIOD*UNREGISTER):
            print 'Unregistering (not read > 3 days) {}'.format(domain.encode('idna'))
            repository.unregister_domain(domain)
            return

    # Skip domains that have been recently updated
    delta_last_updated = repository.delta_report_updated(domain)
    if delta_last_updated is not None:
        age = datetime.datetime.now() - delta_last_updated
        if age < datetime.timedelta(seconds=PERIOD):
            print 'Skipping (recently updated) {}'.format(domain.encode('idna'))
            return

    start = time.time()

    existing_report = repository.get_resolution_report(domain)

    if existing_report is None:
        existing_report = {}

    new_report = {}
    for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
        ip_addr, error = tools.resolve(entry['domain-name'])
        if error or not ip_addr or ip_addr is None:
            continue
        new_report[entry['domain-name']] = {
            'ip': ip_addr,
            'tweak': entry['fuzzer'],
        }

    repository.update_resolution_report(domain, new_report)

    delta_report = {'new': [], 'updated': [], 'deleted': []}
    for (dom, data) in new_report.items():

        try:
            new_ip = data['ip']
        except TypeError:
            # handle old-style ip-only reports
            new_ip = data

        if dom in existing_report.keys():

            try:
                existing_ip = existing_report[dom]['ip']
            except TypeError:
                # handle old-style ip-only reports
                existing_ip = existing_report[dom]

            if new_ip != existing_ip:
                delta_report['updated'].append(
                    (dom, existing_ip, new_ip)
                )
        else:

            delta_report['new'].append((dom, new_ip))

    for dom in existing_report.keys():
        if dom not in new_report.keys():
            delta_report['deleted'].append(dom)

    repository.update_delta_report(domain, delta_report)

    print 'Updated deltas for {} in {} seconds'.format(
        domain.encode('idna'), time.time() - start
    )


def main():
    """Main code for worker."""
    while True:

        print 'Starting delta processing...'

        start = time.time()

        domains_iter = repository.iregistered_domains()

        while True:
            try:
                domain = domains_iter.next()
            except StopIteration:
                break

            process_domain(domain)

        print 'All deltas processed in {} seconds'.format(
            round(time.time() - start, 2)
        )

        time.sleep(60)


if __name__ == '__main__':
    main()
