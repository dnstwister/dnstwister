"""Stats logging to stdout."""
import time

import main


if __name__ == '__main__':

    while True:
        print ','.join(map(str, ('deltas', main.db.deltas.count())))
        print ','.join(map(str, ('report', main.db.reports.count())))
        time.sleep(60)
