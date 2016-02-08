"""Storage of results for comparison and CUD alerting."""
import datetime
import hashlib
import os
import psycopg2.extras
import psycopg2.pool
import urlparse


urlparse.uses_netloc.append('postgres')
DB_URL = urlparse.urlparse(os.environ['DATABASE_URL'])
DB = None


def cursor():
    """Return a database cursor."""
    global DB
    if DB is None or DB.closed != 0:
        db = psycopg2.connect(
            database=DB_URL.path[1:],
            user=DB_URL.username,
            password=DB_URL.password,
            host=DB_URL.hostname,
            port=DB_URL.port,
        )
        db.autocommit = True
        psycopg2.extras.register_hstore(db)
        DB = db
    cursor = DB.cursor()
    return cursor


def report_set(domain, new, updated, generated=None):
    """Store a CRUD report for a domain."""
    if generated is None:
        generated = datetime.datetime.now()
    with cursor() as cur:
        if stored_exists(domain):
            cur.execute("""
                UPDATE reports
                SET (new, updated, generated) = (%s, %s, %s)
                WHERE domain = (%s);
            """, (new, updated, generated, domain))
        else:
            cur.execute("""
                INSERT INTO reports (domain, new, updated, generated)
                VALUES (%s, %s, %s, %s);
            """, (domain, new, updated, generated))


def stored_set(domain, result, updated=None):
    """Store a result for a domain."""
    if updated is None:
        updated = datetime.datetime.now()
    with cursor() as cur:
        if stored_exists(domain):
            cur.execute("""
                UPDATE stored
                SET (result, updated) = (%s, %s)
                WHERE domain = (%s);
            """, (result, updated, domain))
        else:
            cur.execute("""
                INSERT INTO stored (domain, result, updated)
                VALUES (%s, %s, %s);
            """, (domain, result, updated))


def stored_exists(domain):
    """Return whether a domain has results recorded."""
    with cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM stored
            WHERE domain = (%s)
            LIMIT 1;
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
        result = cur.fetchone()
        if result is None:
            return
        return result[0]


def stored_oldest():
    """Return the domain that hasn't been checked for longest time."""
    with cursor() as cur:
        cur.execute("""
            SELECT domain
            FROM stored
            ORDER BY updated ASC
            LIMIT 1
        """)
        result = cur.fetchone()
        if result is None:
            return
        return result[0]


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
        cur.commit()

    return auth
