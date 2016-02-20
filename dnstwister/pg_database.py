"""Storage of results for comparison and CUD alerting."""
import os
import psycopg2.extras
import psycopg2.pool
import urlparse


class _PGDatabase(object):
    """Pseudo-ORM for a postgres database."""
    def __init__(self):
        self._db = None

    @property
    def cursor(self):
        """Return a database cursor."""
        if self._db is None or self._db.closed != 0:
            urlparse.uses_netloc.append('postgres')
            db_url = urlparse.urlparse(os.environ['DATABASE_URL'])
            db = psycopg2.connect(
                database=db_url.path[1:],
                user=db_url.username,
                password=db_url.password,
                host=db_url.hostname,
                port=db_url.port,
            )
            psycopg2.extras.register_hstore(db)
            self._db = db
        cur = self._db.cursor()
        return cur

    def _commit(self):
        """Commit the current transaction."""
        self._db.commit()


class _Reports(_PGDatabase):
    """Reports access."""
    def oldest(self):
        """Return the domain that hasn't been checked for the longest time.

        Returns (domain, update_date) or None.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT domain, updated
                FROM report
                ORDER BY updated ASC
                LIMIT 1
            """)
            result = cur.fetchone()
            if result is None:
                return
            return result

    def update(self, domain, data, updated):
        """Update the latest result for a domain."""
        with self.cursor as cur:
            cur.execute("""
                UPDATE report
                SET (data, updated) = (%s, %s)
                WHERE domain = (%s);
            """, (data, updated, domain))
        self._commit()

    def new(self, domain, start_date):
        """Create a new entry with no report.

        By using a date in the past you can push the report to the top of the
        queue.
        """
        with self.cursor as cur:
            cur.execute("""
                INSERT INTO report (domain, data, updated)
                VALUES (%s, %s, %s);
            """, (domain, {}, start_date))
        self._commit()

    def get(self, domain):
        """Return the report for a domain, or None if no domain."""
        with self.cursor as cur:
            cur.execute("""
                SELECT data
                FROM report
                WHERE domain = (%s);
            """, (domain,))
            result = cur.fetchone()
            if result is None:
                return
            return result[0]


# Singletons
reports = _Reports()
