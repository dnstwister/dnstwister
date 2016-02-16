"""Updates atom feeds."""
import base64
import datetime
import requests
import time

import db
import tools


# Time in seconds between re-processing a domain.
PERIOD = 60#86400


if __name__ == '__main__':
    while True:

        try:
            start = time.time()

            # Pick the oldest domain.
            with db.cursor() as cursor:

                threshold = (
                    datetime.datetime.now() -
                    datetime.timedelta(seconds=PERIOD)
                )

                # Get the first entry with an updated date older than the
                # threshold.
                cursor.execute("""
                    SELECT domain, updated
                    FROM stored
                    WHERE updated < (%s)
                    ORDER BY updated ASC
                    LIMIT 1
                """, (threshold,))

                result = cursor.fetchone()

                # If we're idle, that's great.
                if result is None:
                    time.sleep(1)
                    continue

                domain, updated = result

                age = (datetime.datetime.now() - updated).total_seconds()

            # Generate a new report.
            latest = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:

                # Reuse the public API
                res = requests.get(
                    '/ip/{}'.format(base64.b64encode(entry['domain-name']))
                ).json()

                ip, error = res['ip'], res['error']
                if error or not ip or ip is None:
                    continue
                latest[entry['domain-name']] = ip

            # Update the "latest" version of the report.
            db.stored_set(domain, latest)

            print ','.join(map(str, (
                domain, age, time.time() - start
            )))

        except Exception as ex:
            db.DB = None
            time.sleep(1)
            print 'crashed... {}'.format(ex)
