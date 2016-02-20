"""Database provisioning."""
import datetime
import psycopg2.extras
import sys
import urlparse


def setup(new_conn, cursor):
    """Bootstrap the database on import.

    Assumes no existing database.
    """
    print 'Setting up hstore'
    cursor.execute("""CREATE EXTENSION hstore;""")

    psycopg2.extras.register_hstore(new_conn)

    print 'Creating "report" table.'
    cursor.execute("""
        CREATE TABLE report
            (
                domain varchar PRIMARY KEY,
                data hstore,
                generated timestamp
            );
    """)

    print 'Creating "delta" table.'
    cursor.execute("""
        CREATE TABLE delta
            (
                domain varchar PRIMARY KEY,
                new hstore,
                updated hstore,
                deleted hstore,
                generated timestamp
            );
    """)

    # Some test data
    print 'Injecting some test data.'
    cursor.execute("""
        INSERT INTO report (domain, data, generated)
        VALUES (%s, %s, %s);
    """, (
        'www.example.com', {},
        datetime.datetime.now() - datetime.timedelta(days=5)
    ))
    cursor.execute("""
        INSERT INTO report (domain, data, generated)
        VALUES (%s, %s, %s);
    """, (
        'www.thisismyrobot.com', {},
        datetime.datetime.now() - datetime.timedelta(days=10)
    ))


if __name__ == '__main__':

    db_url = sys.argv[-1]
    if not db_url.startswith('postgres'):
        raise Exception('Missing database url')

    urlparse.uses_netloc.append("postgres")
    new_url = urlparse.urlparse(db_url)

    new_conn = psycopg2.connect(
        database=new_url.path[1:],
        user=new_url.username,
        password=new_url.password,
        host=new_url.hostname,
        port=new_url.port
    )

    new_cursor = new_conn.cursor()

    setup(new_conn, new_cursor)

    new_conn.commit()
    new_cursor.close()
    new_conn.close()
