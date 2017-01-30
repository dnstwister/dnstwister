"""Key-value store using jsonb in postgres. """
import datetime
import os
import urlparse

import psycopg2.extras
import psycopg2.pool
import zope.interface

from dnstwister.storage import interfaces


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DB_PATH_ENV_VAR = 'STATS_DB_URL'


def resetonfail(func):
    """Decorator to ensure that the transaction is rolled back on failure."""
    def wrapped(instance, *args, **kwargs):
        """ Wrapper to do DB reset."""
        try:
            return func(instance, *args, **kwargs)
        except:
            instance.reset()
            raise
    return wrapped


class PgKvDatabase(object):
    """Postgres key-value storage implementation."""
    zope.interface.implements(interfaces.IKeyValueDB)

    def __init__(self):
        self._db = None

    @property
    def cursor(self):
        """Return a database cursor."""
        if self._db is None or self._db.closed != 0:
            print 'Creating postgres database connection.'
            urlparse.uses_netloc.append('postgres')
            db_url = urlparse.urlparse(os.environ[DB_PATH_ENV_VAR])
            db = psycopg2.connect(
                database=db_url.path[1:],
                user=db_url.username,
                password=db_url.password,
                host=db_url.hostname,
                port=db_url.port,
            )
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
    def ikeys(self, prefix):
        """Return an iterator of all the keys starting with a prefix,
        in the database.
        """
        with self.cursor as cur:
            cur.execute("""
                SELECT jsonb_object_keys(data)
                FROM data
                WHERE prefix = %s;
            """, (prefix,))
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                yield row[0]

    @resetonfail
    def delete(self, prefix, key):
        """Delete by key."""
        with self.cursor as cur:
            cur.execute("""
                UPDATE data
                SET data = data - %s
                WHERE prefix = %s;
            """, (key, prefix))
            self._commit()

    @resetonfail
    def set(self, prefix, key, value):
        """Insert/Update the value for a key."""
        with self.cursor as cur:
            cur.execute("""
                UPDATE data
                SET data = jsonb_set(data, %s, %s, true)
                WHERE prefix = %s;
            """, ('{' + key + '}', psycopg2.extras.Json(value), prefix))
            self._commit()

    @resetonfail
    def get(self, prefix, key):
        """Return the value for key, or None if no value."""
        with self.cursor as cur:
            cur.execute("""
                SELECT data -> %s
                FROM data
                WHERE prefix = %s;
            """, (key, prefix))
            result = cur.fetchone()
            if result is None:
                return
            return result[0]

    @staticmethod
    def to_db_datetime(datetime_obj):
        """Convert a datetime object to db datetime data."""
        return datetime_obj.strftime(DATETIME_FORMAT)

    @staticmethod
    def from_db_datetime(datetime_data):
        """Convert datetime data from db to a datetime object."""
        return datetime.datetime.strptime(datetime_data, DATETIME_FORMAT)
