"""Storage of results for comparison and CUD alerting."""
import datetime
import hashlib
import os
import psycopg2.extras
import psycopg2.pool
import urlparse


DB = None


def cursor():
    """Return a database cursor."""
    global DB
    if DB is None or DB.closed != 0:
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
        DB = db
    cur = DB.cursor()
    return cur


def stored_set(domain, latest, updated=None):
    """Store the latest result for a domain."""
    if updated is None:
        updated = datetime.datetime.now()
    with cursor() as cur:
        if stored_exists(domain):
            cur.execute("""
                UPDATE stored
                SET (latest, updated) = (%s, %s)
                WHERE domain = (%s);
            """, (latest, updated, domain))
        else:
            cur.execute("""
                INSERT INTO stored (domain, last_read, latest, updated)
                VALUES (%s, %s, %s, %s);
            """, (domain, {}, latest, updated))
    DB.commit()


def stored_switch(domain):
    """Copy the latest to the last_read.

    Triggered when the RSS feed is read.
    """
    DB.commit()
    last_read, latest = stored_get(domain)
    with cursor() as cur:
        cur.execute("""
            UPDATE stored
            SET (last_read) = (%s)
            WHERE domain = (%s);
        """, (latest, domain))
    DB.commit()


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
            SELECT last_read, latest
            FROM stored
            WHERE domain = (%s);
        """, (domain,))
        result = cur.fetchone()
        if result is None:
            return
        return result


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
    DB.commit()

    return auth
