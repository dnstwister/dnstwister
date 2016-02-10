"""Updates atom feeds."""
import datetime
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
                    SELECT domain
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

                domain = result[0]

            # Generate a new report.
            latest = {}
            for entry in tools.analyse(domain)[1]['fuzzy_domains'][1:]:
                ip, error = tools.resolve(entry['domain-name'])
                if error or not ip or ip is None:
                    continue
                latest[entry['domain-name']] = ip

            # Update the "latest" version of the report.
            db.stored_set(domain, latest)

            print ','.join(map(str, (
                domain, time.time() - start
            )))

        except Exception as ex:
            db.DB = None
            time.sleep(1)
            print 'crashed... {}'.format(ex)
