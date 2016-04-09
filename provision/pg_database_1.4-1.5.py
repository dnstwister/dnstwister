"""Database provisioning."""
import psycopg2.extras
import sys
import urlparse


def bump(new_conn, cursor):
    """Bump the database between releases."""
    # Move to ':' prefixes
    cursor.execute("""
        SELECT key from data;
    """)
    v1_4_keys = [row[0]
                 for row
                 in cursor.fetchall()]

    v1_5_keys = [':'.join(key.rsplit('_', 1))
                 for key
                 in v1_4_keys]

    for (old, new) in zip(v1_4_keys, v1_5_keys):
        try:
            cursor.execute("""
                UPDATE data
                SET (key) = (%s)
                WHERE key = (%s);
            """, (new, old))
            new_conn.commit()
        except Exception as ex:
            new_conn.rollback()
            print 'skipped ', old, new, ex


if __name__ == '__main__':

    db_url = sys.argv[-1]
    if not db_url.startswith('postgres'):
        raise Exception('Missing database url')

    urlparse.uses_netloc.append('postgres')
    new_url = urlparse.urlparse(db_url)

    new_conn = psycopg2.connect(
        database=new_url.path[1:],
        user=new_url.username,
        password=new_url.password,
        host=new_url.hostname,
        port=new_url.port
    )

    new_cursor = new_conn.cursor()

    bump(new_conn, new_cursor)

    new_conn.commit()
    new_cursor.close()
    new_conn.close()
