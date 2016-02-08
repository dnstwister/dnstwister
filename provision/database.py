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

    print 'Creating "stored" table.'
    cursor.execute("""
        CREATE TABLE stored
            (domain varchar PRIMARY KEY, result hstore, updated timestamp);
    """)

    print 'Creating "reports" table.'
    cursor.execute("""
        CREATE TABLE reports
            (
                domain varchar PRIMARY KEY,
                new hstore,
                updated hstore,
                generated timestamp
            );
    """)

    # Subscriptions
    print 'Creating "subscriptions" table.'
    cursor.execute("""
        CREATE TABLE subscriptions
            (auth_hash bytea PRIMARY KEY, domain varchar, expires timestamp);
    """)

    # Some test data
    print 'Injecting some test data.'
    cursor.execute("""
        INSERT INTO stored (domain, result, updated)
        VALUES (%s, %s, %s);
    """, (
        'www.example.com', {},
        datetime.datetime.now() - datetime.timedelta(days=5)
    ))
    cursor.execute("""
        INSERT INTO stored (domain, result, updated)
        VALUES (%s, %s, %s);
    """, (
        'www.thisismyrobot.com', {},
        datetime.datetime.now() - datetime.timedelta(days=10)
    ))


def migrate(conn_new, conn_old):
    """This is where I'd load in the previous database's data.
    """
    pass


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
