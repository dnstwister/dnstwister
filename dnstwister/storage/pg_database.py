"""Storage of results for comparison and CUD alerting."""
import os
import psycopg2.extras
import psycopg2.pool
import urlparse
import zope.interface

import interfaces


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

    @resetonfail
    def iter(self, *keys):
        """Iterate all the rows, returning tuples of values for the keys."""
        whitelist = set(('domain', 'data', 'generated')) # injection...
        with self.cursor as cur:
            cur.execute("""
                SELECT {columns}
                FROM report;
            """.format(columns=','.join(tuple(set(keys) & whitelist))))
            while True:
                next = cur.fetchone()
                if next is None:
                    break
                yield next


class _Reports(_PGDatabase):
    """Reports access."""
    zope.interface.implements(interfaces.IReports)

    @resetonfail
    def set(self, domain, data, generated):
        """Insert/Update the resolution report for a domain."""
        with self.cursor as cur:
            try:
                cur.execute("""
                    INSERT INTO report (domain, data, generated)
                    VALUES (%s, %s, %s);
                """, (domain, psycopg2.extras.Json(data), generated))
            except psycopg2.IntegrityError as ex:
                print 'ex detail', ex.pgcode
                cur.execute("""
                    UPDATE report
                    SET (data, generated) = (%s, %s)
                    WHERE domain = (%s);
                """, (psycopg2.extras.Json(data), generated, domain))
        self._commit()

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


class _Deltas(_PGDatabase):
    """Report-deltas access."""
    zope.interface.implements(interfaces.IDeltas)

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
        """Insert/Update the deltas for a domain."""
        with self.cursor as cur:
            try:
                cur.execute("""
                    INSERT INTO delta (domain, deltas, generated)
                    VALUES (%s, %s, %s);
                """, (domain, psycopg2.extras.Json(deltas), generated))
            except psycopg2.IntegrityError as ex:
                print 'ex detail', ex.pgcode
                cur.execute("""
                    UPDATE delta
                    SET (deltas, generated) = (%s, %s)
                    WHERE domain = (%s);
                """, (psycopg2.extras.Json(deltas), generated, domain))

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


# Singletons
reports = _Reports()
deltas = _Deltas()
