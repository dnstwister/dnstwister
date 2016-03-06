"""Database provisioning."""
import psycopg2.extras
import sys
import urlparse


def setup(new_conn, cursor):
    """Bootstrap the database.

    Assumes no existing database.
    """
    print 'Setting up jsonb...'
    psycopg2.extras.register_json(new_conn, name='jsonb')

    print 'Creating "data" table...'
    cursor.execute("""
        CREATE TABLE data
            (
                key varchar PRIMARY KEY,
                value jsonb
            );
    """)

    print 'Importing old data...'
    cursor.execute("""
        delete from data
    """)
    new_conn.commit()

    sys.path.append('..')
    import dnstwister.repository as repository

    # Domains for reporting
    cursor.execute("""
        select domain from report
    """)
    rows = cursor.fetchall()

    for row in rows:
        repository.register_domain(row[0])

    # Reports
    cursor.execute("""
        select * from report
    """)
    rows = cursor.fetchall()

    for row in rows:
        repository.update_resolution_report(*row)

    # Deltas
    cursor.execute("""
        select * from delta
    """)
    rows = cursor.fetchall()

    for row in rows:
        repository.update_delta_report(*row)


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

    setup(new_conn, new_cursor)

    new_conn.commit()
    new_cursor.close()
    new_conn.close()
