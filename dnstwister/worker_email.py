"""Updates atom feeds."""
import os
import sys
sys.path.insert(0, os.getcwd())

import binascii
import datetime
import time
import traceback

from dnstwister import emailer, repository
import dnstwister.tools.email as email_tools

# Time in seconds between sending emails for a subscription.
PERIOD = 86400
ANALYSIS_ROOT = 'https://dnstwister.report/analyse/{}'


def process_sub(sub_id, detail):
    """Process a subscription."""

    domain = detail['domain']
    email_address = detail['email_address']

    # Ensure the domain is registered for reporting, register if not.
    repository.register_domain(domain)

    # Mark delta report as "read" so it's not unsubscribed.
    repository.mark_delta_report_as_read(domain)

    # Don't send more than once every 24 hours
    last_sent = repository.email_last_send_for_sub(sub_id)
    if last_sent is not None:
        age_last_sent = datetime.datetime.now() - last_sent
        if age_last_sent < datetime.timedelta(seconds=PERIOD):
            print 'Skipping {} + {}, < 24h hours'.format(
                email_address, domain
            )
            return

    # Grab the delta
    delta = repository.get_delta_report(domain)
    if delta is None:
        print 'Skipping {} + {}, no delta report yet'.format(
            email_address, domain
        )
        return

    # Grab the delta report update time.
    delta_updated = repository.delta_report_updated(domain)

    # If the delta report was updated > 23 hours ago, we're too close to the
    # next delta report. This means we should hold off so we don't send the
    # same delta report twice.
    if delta_updated is not None:
        age_delta_updated = datetime.datetime.now() - delta_updated
        if age_delta_updated > datetime.timedelta(hours=23):
            print 'Skipping {} + {}, delta > 23h hours old'.format(
                email_address, domain
            )
            return

    # Don't email if no changes
    new = delta['new'] if len(delta['new']) > 0 else None
    updated = delta['updated'] if len(delta['updated']) > 0 else None
    deleted = delta['deleted'] if len(delta['deleted']) > 0 else None

    if new is updated is deleted is None:
        print 'Skipping {} + {}, no changes'.format(
            email_address, domain
        )
        return

    # Add analysis links
    if new is not None:
        new = [(dom, ip, ANALYSIS_ROOT.format(binascii.hexlify(dom)))
               for (dom, ip)
               in new]

    if updated is not None:
        updated = [(dom, old_ip, new_ip, ANALYSIS_ROOT.format(binascii.hexlify(dom)))
                   for (dom, old_ip, new_ip)
                   in updated]

    # Email
    body = email_tools.render_email(
        'report.html',
        domain=domain,
        new=new,
        updated=updated,
        deleted=deleted,
        unsubscribe_link='https://dnstwister.report/email/unsubscribe/{}'.format(sub_id)
    )

    # Mark as emailed to ensure we don't flood if there's an error after the
    # actual email has been sent.
    repository.update_last_email_sub_sent_date(sub_id)

    emailer.send(
        email_address, 'dnstwister report for {}'.format(domain), body
    )
    print 'Emailed delta for {} to {}'.format(domain, email_address)


if __name__ == '__main__':
    while True:

        subs_iter = repository.isubscriptions()

        while True:

            try:
                sub = subs_iter.next()
            except StopIteration:
                print 'All subs processed'
                break

            if sub is None:
                break

            sub_id, sub_detail = sub

            try:
                process_sub(sub_id, sub_detail)
            except:
                print 'Skipping {}, exception:\n {}'.format(
                    sub_id, traceback.format_exc()
                )

            time.sleep(1)

        time.sleep(60)
