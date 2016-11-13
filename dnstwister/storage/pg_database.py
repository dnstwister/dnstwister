"""Storage of results for comparison and CUD alerting."""
import os
import urlparse

import psycopg2.extras
import psycopg2.pool
import zope.interface

from dnstwister.storage import interfaces


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


class PGDatabase(object):
    """Postgres database storage implementation."""
    zope.interface.implements(interfaces.IKeyValueDB)

    def __init__(self):
        self._db = None

    @property
    def cursor(self):
        """Return a database cursor."""
        if self._db is None or self._db.closed != 0:
            print 'Creating postgres database connection.'
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

    def _rollback(self):
        """Rollback the current transaction."""
        self._db.rollback()

    def reset(self):
        """Reset the database transaction and connection."""
        try:
            self._db.rollback()
        except:
            # If we can't rollback, let's assume something pretty bad has
            # happened :(
            self._db = None

    @resetonfail
    def ikeys(self, prefix=''):
        """Return an iterator of all the keys in the database.

        Optionally filter by key prefix.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT key
                FROM data;
            """)
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                if row[0].startswith(prefix + ':'):
                    yield row[0]

    @resetonfail
    def delete(self, key):
        """Delete by key."""
        with self.cursor as cur:
            cur.execute("""
                DELETE FROM data
                WHERE key = (%s);
            """, (key,))
            self._commit()

    @resetonfail
    def set(self, key, value):
        """Insert/Update the value for a key."""
        with self.cursor as cur:
            try:
                cur.execute("""
                    INSERT INTO data (key, value)
                    VALUES (%s, %s);
                """, (key, psycopg2.extras.Json(value)))
            except psycopg2.IntegrityError:
                self._rollback()
                cur.execute("""
                    UPDATE data
                    SET (value) = (%s)
                    WHERE key = (%s);
                """, (psycopg2.extras.Json(value), key))
            self._commit()

    @resetonfail
    def get(self, key):
        """Return the value for key, or None if no value."""
        with self.cursor as cur:
            cur.execute("""
                SELECT value
                FROM data
                WHERE key = (%s);
            """, (key,))
            result = cur.fetchone()
            if result is None:
                return
            return result[0]
