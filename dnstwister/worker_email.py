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

# Multiplier on period to remove unverified links.
UNVERIFIED_THRESH = 7


if __name__ == '__main__':
    while True:

        subs_iter = repository.isubscriptions(list_all=True)

        while True:
            try:
                sub = subs_iter.next()
            except StopIteration:
                break

            sub_id, sub_detail = sub

            domain = sub_detail['domain']
            email = sub_detail['email']

            # Clear up long-time unverified subscriptions
            if domain is None:
                created = datetime.datetime.strptime(
                    sub_detail['created'], '%Y-%m-%dT%H:%M:%SZ'
                )
                staged_age = datetime.datetime.now() - created
                if staged_age > datetime.timedelta(seconds=PERIOD*UNVERIFIED_THRESH):
                    repository.unsubscribe(sub_id)
                    print 'Unsubscribing {} + {}, never verified'.format(
                        email, domain
                    )
                else:
                    print 'Skipping a sub for {}, not verified yet'.format(email)
                continue

            # Don't send more than once every 24 hours
            if sub_detail['last_sent'] is not None:
                last_sent = datetime.datetime.strptime(
                    sub_detail['last_sent'], '%Y-%m-%dT%H:%M:%SZ'
                )
                age_last_sent = datetime.datetime.now() - last_sent
                if age_last_sent < datetime.timedelta(seconds=PERIOD):
                    print 'Skipping {} + {}, < 24h hours'.format(
                        email, domain
                    )
                    continue

            # Grab the delta
            delta = repository.get_delta_report(domain)
            if delta is None:
                print 'Skipping {} + {}, no delta report yet'.format(
                    email, domain
                )
                continue

            # Email
            print 'Emailing delta for {} to {}'.format(domain, email)
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

            # Mark as emailed
            repository.email_sent(sub_id)

            time.sleep(1)

        time.sleep(60)
