"""Database provisioning."""
import psycopg2
import sys
import urlparse


def setup(cursor):
    """Bootstrap the database on import.

    Assumes no existing database.
    """
    print 'Setting up hstore'
    cursor.execute("""CREATE EXTENSION hstore;""")

    print 'Creating "stored" table.'
    cursor.execute("""
        CREATE TABLE stored
            (domain varchar PRIMARY KEY, result hstore, updated timestamp);
    """)

    # Subscriptions
    print 'Creating "subscriptions" table.'
    cursor.execute("""
        CREATE TABLE subscriptions
            (auth_hash bytea PRIMARY KEY, domain varchar, expires timestamp);
    """)


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

    setup(new_cursor)

    new_conn.commit()
    new_cursor.close()
    new_conn.close()
