"""Updates atom feeds."""
import datetime
import time
import traceback

from dnstwister import emailer, repository, tools, stats_store
import dnstwister.tools.email as email_tools
import dnstwister.tools.template as template_tools
import dnstwister.configuration.features as feature_flags


# Time in seconds between sending emails for a subscription.
PERIOD = 86400
ANALYSIS_ROOT = 'https://dnstwister.report/analyse/{}'


def remove_noisy(delta):
    """Strip out all domains identified as noisy."""
    if not feature_flags.enable_noisy_domains():
        return delta

    filtered_delta = {}
    for change in delta.keys():
        filtered_delta[change] = []
        for result in delta[change]:
            domain = result[0]
            if not stats_store.is_noisy(domain):
                filtered_delta[change].append(result)

    return filtered_delta


def process_sub(sub_id, detail):
    """Process a subscription."""
    domain = detail['domain']
    email_address = detail['email_address']
    
    hide_noisy = False
    try:
        hide_noisy = bool(detail['hide_noisy'])
    except KeyError:
        pass

    sub_log = sub_id[:10]

    # Ensure the domain is registered for reporting, register if not.
    repository.register_domain(domain)

    # Mark delta report as "read" so it's not unsubscribed.
    repository.mark_delta_report_as_read(domain)

    # Don't send more than once every 24 hours
    last_sent = repository.email_last_send_for_sub(sub_id)
    if last_sent is not None:
        age_last_sent = datetime.datetime.now() - last_sent
        if age_last_sent < datetime.timedelta(seconds=PERIOD):
            print '<24h: {}'.format(sub_log)
            return

    # Grab the delta
    delta = repository.get_delta_report(domain)
    if delta is None:
        print 'No delta: {}'.format(sub_log)
        return

    # Grab the delta report update time.
    delta_updated = repository.delta_report_updated(domain)

    # If the delta report was updated > 23 hours ago, we're too close to the
    # next delta report. This means we should hold off so we don't send the
    # same delta report twice.
    if delta_updated is not None:
        age_delta_updated = datetime.datetime.now() - delta_updated
        if age_delta_updated > datetime.timedelta(hours=23):
            print '>23h: {}'.format(sub_log)
            return

    # Filter out noisy domains if that's the user's preference.
    if hide_noisy:
        delta = remove_noisy(delta)

    # Don't email if no changes
    new = delta['new'] if len(delta['new']) > 0 else None
    updated = delta['updated'] if len(delta['updated']) > 0 else None
    deleted = delta['deleted'] if len(delta['deleted']) > 0 else None

    if new is updated is deleted is None:
        print 'Empty: {}'.format(sub_log)
        return

    # Add analysis links
    if new is not None:
        new = [(dom, ip, ANALYSIS_ROOT.format(tools.encode_domain(dom)))
               for (dom, ip)
               in new]

    if updated is not None:
        updated = [(dom, old_ip, new_ip, ANALYSIS_ROOT.format(tools.encode_domain(dom)))
                   for (dom, old_ip, new_ip)
                   in updated]

    # Email
    noisy_link = None
    if hide_noisy and feature_flags.enable_noisy_domains():
        noisy_link = 'https://dnstwister.report/email/{}/noisy'.format(sub_id)

    body = email_tools.render_email(
        'report.html',
        domain=domain,
        new=new,
        updated=updated,
        deleted=deleted,
        unsubscribe_link='https://dnstwister.report/email/unsubscribe/{}'.format(sub_id),
        noisy_link=noisy_link
    )

    # Mark as emailed to ensure we don't flood if there's an error after the
    # actual email has been sent.
    repository.update_last_email_sub_sent_date(sub_id)

    emailer.send(
        email_address,
        u'dnstwister report for {}'.format(template_tools.domain_renderer(domain)),
        body
    )
    print 'Sent: {}'.format(sub_log)


def main():
    """Main code for worker."""
    while True:

        start = time.time()

        subs_iter = repository.isubscriptions()

        while True:

            try:
                sub = subs_iter.next()
            except StopIteration:
                print 'All subs processed in {} seconds'.format(
                    round(time.time() - start, 2)
                )
                break

            if sub is None:
                break

            sub_id, sub_detail = sub

            try:
                process_sub(sub_id, sub_detail)
            except:
                print u'Skipping {}, exception:\n {}'.format(
                    sub_id, traceback.format_exc()
                )

            time.sleep(1)

        time.sleep(datetime.timedelta(minutes=15).total_seconds())


if __name__ == '__main__':
    main()
