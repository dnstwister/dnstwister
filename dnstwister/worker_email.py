"""Updates atom feeds."""
import os
import sys
sys.path.insert(0, os.getcwd())

import datetime
import time
import traceback

from dnstwister import emailer, repository
import dnstwister.tools.email as email_tools

# Time in seconds between sending emails for a subscription.
PERIOD = 86400


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

    # Don't email if no changes
    new = delta['new'] if len(delta['new']) > 0 else None
    updated = delta['updated'] if len(delta['updated']) > 0 else None
    deleted = delta['deleted'] if len(delta['deleted']) > 0 else None

    if new is updated is deleted is None:
        print 'Skipping {} + {}, no changes'.format(
            email_address, domain
        )
        return

    # Email
    body = email_tools.render_email(
        'report.html',
        domain=domain,
        updated_date='now-ish',
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
                break

            if sub is None:
                break

            sub_id, sub_detail = sub

            try:
                process_sub(sub_id, sub_detail)
                time.sleep(1)
            except:
                print 'Skipping {}, exception:\n {}'.format(
                    sub_id, traceback.format_exc()
                )

                # Temporary to tidy up test DB
                repository.unsubscribe(sub_id)

                time.sleep(1)

        time.sleep(60)
