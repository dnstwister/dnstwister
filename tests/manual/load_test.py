# Manual test script to assist with load testing.
#
# Usage:
#           python load_test.py [host:port]
#
# Eg:
#           python load_test.py http://localhost:5000
#
import binascii
import datetime
import multiprocessing
import sys

import requests


DOMAIN_TEMPLATE = '{}zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzppieo.com'
DOMAIN_TEMPLATE = 'ww{}.example.com'
CLIENTS = 20


def request(args):
    host, domain = args
    url = '{}/search/{}'.format(
        host,
        binascii.hexlify(domain.encode('idna'))
    )

    start = datetime.datetime.now()
    requests.get(url).content
    end = datetime.datetime.now()

    print url, (end - start).total_seconds()


def test(host):
    start = datetime.datetime.now()
    pool = multiprocessing.Pool(CLIENTS)
    args = [(host, DOMAIN_TEMPLATE.format(i))
            for i
            in range(CLIENTS)]
    pool.map(request, args)
    end = datetime.datetime.now()
    print '{} requests took {} seconds'.format(
        CLIENTS,
        (end - start).total_seconds()
    )


if __name__ == '__main__':
    host = sys.argv[1]
    test(host)
