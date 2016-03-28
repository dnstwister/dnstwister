"""Updates atom feeds."""
import os
import sys
sys.path.insert(0, os.getcwd())

import datetime
import time

from dnstwister import emailer, repository

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
                created = sub_detail['created']
                staged_age = datetime.datetime.now() - created
                if staged_age > datetime.timedelta(seconds=PERIOD*UNVERIFIED_THRESH):
                    repository.unsubscribe(sub_id)
                    print 'Unsubscribing {} + {}, never verified'.format(
                        email, domain
                    )
                continue

            # Don't send more than once every 24 hours
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
            emailer.send(
                email, 'dnstwister report for {}'.format(domain),
                str(delta),
            )

            # Mark as emailed
            repository.email_sent(sub_id)

            time.sleep(1)

        time.sleep(60)
