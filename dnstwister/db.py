"""Storage of results for comparison and CUD alerting."""
import contextlib
import datetime
import hashlib
import json
import os
import psycopg2.pool
import urlparse


urlparse.uses_netloc.append('postgres')
DB_URL = urlparse.urlparse(os.environ['DATABASE_URL'])

DB_CONN_POOL = psycopg2.pool.ThreadedConnectionPool(
    1,
    10,
    database=DB_URL.path[1:],
    user=DB_URL.username,
    password=DB_URL.password,
    host=DB_URL.hostname,
    port=DB_URL.port,
)


@contextlib.contextmanager
def cursor():
    """Return a database cursor."""
    try:
        conn = DB_CONN_POOL.getconn()
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
    finally:
        DB_CONN_POOL.putconn(conn)


def stored_set(domain, result):
    """Store a result for a domain."""
    with cursor() as cur:
        if stored_exists(domain):
            cur.execute("""
                UPDATE stored
                SET result = (%s)
                WHERE domain = (%s);
            """, (json.dumps(result), domain))
        else:
            cur.execute("""
                INSERT INTO stored (domain, result)
                VALUES (%s, %s);
            """, (domain, json.dumps(result)))


def stored_exists(domain):
    """Return whether a domain has results recorded."""
    with cursor() as cur:
        cur.execute("""
            SELECT domain
            FROM stored
            where domain = (%s);
        """, (domain,))
        return cur.fetchone() is not None


def stored_get(domain):
    """Return stored results for a domain or None if none exist."""
    with cursor() as cur:
        cur.execute("""
            SELECT result
            FROM stored
            WHERE domain = (%s);
        """, (domain,))
        (result,) = cur.fetchone()
        if result is None:
            return
        return json.loads(result)


def subscription_new(domain, auth_len=100):
    """Create a new subscription for a domain, return the sub auth string."""
    auth = os.urandom(auth_len).encode('hex')[:auth_len]

    auth_hash = bytearray(hashlib.sha512(auth).digest())
    expires = datetime.datetime.now() + datetime.timedelta(days=365)

    with cursor() as cur:
        cur.execute("""
            INSERT INTO subscriptions (auth_hash, domain, expires)
            VALUES (%s, %s, %s)
        """, (auth_hash, domain, expires))

    return auth
