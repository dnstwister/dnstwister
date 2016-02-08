"""Updates atom feeds."""
import db
import time


if __name__ == '__main__':
    while True:
        oldest_domain = db.stored_oldest()
        print 'Oldest: {}'.format(oldest_domain)
        time.sleep(5)
