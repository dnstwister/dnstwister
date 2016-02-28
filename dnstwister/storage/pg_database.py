"""Storage of results for comparison and CUD alerting."""
import os
import psycopg2.extras
import psycopg2.pool
import urlparse


import base


class _PGDatabase(object):
    """Pseudo-ORM for a postgres database."""
    def __init__(self):
        self._db = None

    @property
    def cursor(self):
        """Return a database cursor."""
        if self._db is None or self._db.closed != 0:
            print 'Creating a DB connection...'
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

    def reset(self):
        """Reset the database transaction and connection."""
        try:
            self._db.rollback()
        except:
            # If we can't rollback, let's assume something pretty bad has
            # happened :(
            self._db = None


def resetonfail(func):
    """Decorator to ensure that the transaction is rolled back on failure.
    """
    def wrapped(instance, *args, **kwargs):
        """ Wrapper to do DB reset."""
        try:
            return func(instance, *args, **kwargs)
        except:
            instance.reset()
            raise
    return wrapped


class _Reports(_PGDatabase):
    """Reports access."""

    @resetonfail
    def oldest(self):
        """Return the domain that hasn't been checked for the longest time.

        Returns (domain, generated_date) or None.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT domain, generated
                FROM report
                ORDER BY generated ASC
                LIMIT 1
            """)
            return cur.fetchone()

    @resetonfail
    def update(self, domain, data, generated):
        """Update the latest result for a domain."""
        with self.cursor as cur:
            if self.exists(domain):
                cur.execute("""
                    UPDATE report
                    SET (data, generated) = (%s, %s)
                    WHERE domain = (%s);
                """, (psycopg2.extras.Json(data), generated, domain))
            else:
                cur.execute("""
                    INSERT INTO report (domain, data, generated)
                    VALUES (%s, %s, %s);
                """, (domain, psycopg2.extras.Json(data), generated))
        self._commit()

    @resetonfail
    def exists(self, domain):
        """Return whether a domain exists in the database, for reports."""
        with self.cursor as cur:
            cur.execute("""
                SELECT
                FROM report
                WHERE domain = (%s);
            """, (domain,))
            return cur.fetchone() is not None

    @resetonfail
    def get(self, domain):
        """Return the report for a domain, or None if no report."""
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

    @resetonfail
    def count(self):
        """Return count of records."""
        with self.cursor as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM report;
            """)
            return int(cur.fetchone()[0])


class _Deltas(_PGDatabase):
    """Report-deltas access."""

    @resetonfail
    def oldest(self):
        """Return the delta that hasn't been updated for the longest time.

        Returns (domain, generated_date) or None.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT domain, generated
                FROM delta
                ORDER BY generated ASC
                LIMIT 1;
            """)
            return cur.fetchone()

    @resetonfail
    def set(self, domain, deltas, generated):
        """Add/update the deltas for a domain."""
        with self.cursor as cur:
            if self.exists(domain):
                cur.execute("""
                    UPDATE delta
                    SET (deltas, generated) = (%s, %s)
                    WHERE domain = (%s);
                """, (psycopg2.extras.Json(deltas), generated, domain))
            else:
                cur.execute("""
                    INSERT INTO delta (domain, deltas, generated)
                    VALUES (%s, %s, %s);
                """, (domain, psycopg2.extras.Json(deltas), generated))
        self._commit()

    @resetonfail
    def get(self, domain):
        """Return the delta info for a domain, or None if no delta."""
        with self.cursor as cur:
            cur.execute("""
                SELECT deltas
                FROM delta
                WHERE domain = (%s);
            """, (domain,))
            result = cur.fetchone()
            if result is None:
                return
            return result[0]

    @resetonfail
    def updated(self, domain):
        """Return the update date for a delta, or None."""
        with self.cursor as cur:
            cur.execute("""
                SELECT generated
                FROM delta
                WHERE domain = (%s);
            """, (domain,))
            result = cur.fetchone()
            if result is None:
                return
            return result[0]

    @resetonfail
    def exists(self, domain):
        """Return whether a domain exists in the database, for delta
        reporting.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT
                FROM delta
                WHERE domain = (%s);
            """, (domain,))
            return cur.fetchone() is not None

    @resetonfail
    def count(self):
        """Return count of records."""
        with self.cursor as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM delta;
            """)
            return int(cur.fetchone()[0])


# ABC registration
base.Reports.register(_Reports)
base.Deltas.register(_Deltas)

# Singletons
reports = _Reports()
deltas = _Deltas()
