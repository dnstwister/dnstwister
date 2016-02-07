"""Storage of results for comparison and CUD alerting."""
import datetime
import hashlib
import json
import os
import psycopg2
import urlparse


urlparse.uses_netloc.append('postgres')
url = urlparse.urlparse(os.environ['DATABASE_URL'])


conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)


def stored_set(domain, result):
    """Store a result for a domain."""
    cur = conn.cursor()
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
    conn.commit()
    cur.close()


def stored_exists(domain):
    """Return whether a domain has results recorded."""
    cur = conn.cursor()
    cur.execute("""
        SELECT domain
        FROM stored
        where domain = (%s);
    """, (domain,))
    return cur.fetchone() is not None


def stored_get(domain):
    """Return stored results for a domain or None if none exist."""
    cur = conn.cursor()
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

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscriptions (auth_hash, domain, expires)
        VALUES (%s, %s, %s)
    """, (auth_hash, domain, expires))
    conn.commit()

    return auth
