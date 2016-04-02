"""Updates atom feeds."""
import os
import sys
sys.path.insert(0, os.getcwd())

import datetime
import time

from dnstwister import emailer, repository
import dnstwister.tools.email as email_tools

# Time in seconds between sending emails for a subscription.
PERIOD = 86400


def process_sub(sub_id, detail):
    """Process a subscription."""

    domain = detail['domain']
    email = detail['email']

    # Ensure the domain is registered for reporting, register if not.
    repository.register_domain(domain)

    # Mark delta report as "read" so it's not unsubscribed.
    repository.mark_delta_report_as_read(domain)

    # Don't send more than once every 24 hours
    if detail['last_sent'] is not None:
        last_sent = datetime.datetime.strptime(
            detail['last_sent'], '%Y-%m-%dT%H:%M:%SZ'
        )
        age_last_sent = datetime.datetime.now() - last_sent
        if age_last_sent < datetime.timedelta(seconds=PERIOD):
            print 'Skipping {} + {}, < 24h hours'.format(
                email, domain
            )
            return

    # Grab the delta
    delta = repository.get_delta_report(domain)
    if delta is None:
        print 'Skipping {} + {}, no delta report yet'.format(
            email, domain
        )
        return

    # Email
    body = email_tools.render_email(
        'report.html',
        domain=domain,
        updated_date='now-ish',
        new=delta['new'] if len(delta['new']) > 0 else None,
        updated=delta['updated'] if len(delta['updated']) > 0 else None,
        deleted=delta['deleted'] if len(delta['deleted']) > 0 else None,
    )
    emailer.send(
        email, 'dnstwister report for {}'.format(domain), body
    )
    print 'Emailed delta for {} to {}'.format(domain, email)

    # Mark as emailed
    repository.email_sent(sub_id)


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
                print 'Skipping {}, exception: {}'.format(
                    sub_id, sys.exc_info()
                )

                time.sleep(10)

        time.sleep(60)
